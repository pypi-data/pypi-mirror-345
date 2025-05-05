import threading
import asyncio
import struct
import logging

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(levelname)s - %(message)s",
)

class AsyncTcpClient:
	def __init__(
		self,
		host: str = '127.0.0.1',
		port: int = 9000,
		on_message=None,
		heartbeat_interval: int = 1,
		reconnect_interval: int = 1,
		heartbeat_message:str = '__PING__',
		name:str = 'AsyncTcpClient',
	):
		self._host = host
		self._port = port
		self._on_message = on_message
		self._heartbeat_interval = heartbeat_interval
		self._reconnect_interval = reconnect_interval
		self._heartbeat_message = heartbeat_message
		self._name = name

		self._latest_message = ''
		self._loop = None
		self._writer = None
		self._reader = None
		self._stop_event = threading.Event()

		def run():
			self._loop = asyncio.new_event_loop()
			asyncio.set_event_loop(self._loop)
			try:
				self._loop.run_until_complete(self._main_loop())
			except Exception as e:
				logging.error(f"[{self._name}] Event loop error: {e}")
			finally:
				self._loop.close()

		self._thread = threading.Thread(target=run, name=f"Thread-{self._name}", daemon=True)

	def start(self):
		if self._thread and not self._thread.is_alive():
			self._thread.start()
			logging.info(f"[{self._name}] Thread started")

	def stop(self):
		self._stop_event.set()
		if self._loop:
			self._loop.call_soon_threadsafe(self._loop.stop)
		logging.info(f"[{self._name}] Stopped client")

	def send(self, message: str):
		try:
			if self._loop and self._writer and not self._writer.is_closing():
				asyncio.run_coroutine_threadsafe(self._send(message), self._loop)
		except Exception as e:
			logging.error(f"[{self._name}] Failed to send message: {e}")

	@property
	def latest_message(self):
		return self._latest_message

	async def _main_loop(self):
		while not self._stop_event.is_set():
			try:
				logging.info(f"[{self._name}] Connecting to {self._host}:{self._port}")
				self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
				logging.info(f"[{self._name}] Connected to server")

				tasks = [
					asyncio.create_task(self._recv_loop()),
					asyncio.create_task(self._heartbeat_loop()),
				]
				await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
			except Exception as e:
				logging.warning(f"[{self._name}] Connection failed: {e}")
			finally:
				if self._writer:
					self._writer.close()
					await self._writer.wait_closed()
				self._writer = None
				self._reader = None
				if not self._stop_event.is_set():
					logging.info(f"[{self._name}] Reconnecting in {self._reconnect_interval} seconds...")
					await asyncio.sleep(self._reconnect_interval)

	async def _send(self, message: str):
		try:
			data = message.encode('utf-8')
			packet = struct.pack(">I", len(data)) + data
			self._writer.write(packet)
			await self._writer.drain()
			await asyncio.sleep(0)
		except Exception as e:
			logging.error(f"[{self._name}] Send error: {e}")

	async def _recv_loop(self):
		try:
			while not self._writer.is_closing():
				header = await self._reader.readexactly(4)
				length = struct.unpack(">I", header)[0]
				data = await self._reader.readexactly(length)
				message = data.decode('utf-8')
				self._latest_message = message
				logging.info(f"[{self._name}] Received message: {message}")
				if self._on_message:
					result = self._on_message(message)
					if asyncio.iscoroutine(result):
						await result
				await asyncio.sleep(0)
		except asyncio.IncompleteReadError:
			logging.warning(f"[{self._name}] Connection closed by server")
		except Exception as e:
			logging.error(f"[{self._name}] Receive error: {e}")

	async def _heartbeat_loop(self):
		try:
			while not self._writer.is_closing():
				await asyncio.sleep(self._heartbeat_interval)
				await self._send(f'{self._heartbeat_message}')
				await asyncio.sleep(0)
		except Exception as e:
			logging.error(f"[{self._name}] Heartbeat error: {e}")
