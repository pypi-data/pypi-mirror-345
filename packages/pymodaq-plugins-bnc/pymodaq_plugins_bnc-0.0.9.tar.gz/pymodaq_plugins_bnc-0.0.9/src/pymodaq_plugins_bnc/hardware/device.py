import telnetlib
import asyncio
import time

class Device:
    def __init__(self, ip, port):
        self.com = telnetlib.Telnet(ip, port, 100)
        self._ip = ip
        self._port = port

    def send(self, msg):
        sent = False
        msg += "\r\n"
        while not sent:
            try:
                self.com.write(msg.encode())
                print("SENDING:", msg)
                sent = True
                time.sleep(0.075)
                message = self.com.read_eager().decode()
                print("RECEIVED:", message)
            except OSError:
                self.com.open(self._ip, self._port, 100)
        return message

    def query(self,msg):
        msg = msg+"?"
        return self.send(msg)

    def set(self, msg, val):
        msg = msg+" "+val
        return self.send(msg)

    def concat(self, commands):
        msg = ""
        for i in commands:
            msg += ":"+i
        return msg


class AsyncDevice:
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self.reader = None
        self.writer = None
        self.lock = asyncio.Lock()
        self.read_timeout = 3.0

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self._ip, self._port)
        print(f"Connected to {self._ip}:{self._port}")

    async def send(self, msg):
        async with self.lock:
            msg += "\r\n"
            print("SENDING:", msg.strip())
            self.writer.write(msg.encode())
            await self.writer.drain()

            try:
                # Wait for 'ok' with a timeout
                response = await asyncio.wait_for(self.reader.readuntil(b"ok"), timeout=self.read_timeout)
                message = response.decode()
                print("RECEIVED:", message.strip())
                return message
            except asyncio.TimeoutError:
                raise TimeoutError(f"No 'ok' received for command: {msg.strip()}")

    async def query(self, msg):
        msg += "?"
        return await self.send(msg)

    async def set(self, msg, val):
        return await self.send(f"{msg} {val}")

    def concat(self, commands):
        return ''.join([f":{cmd}" for cmd in commands])

    async def close(self):
        if self.writer:
            print(f"Closing connection to {self._ip}:{self._port}")
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception as e:
                print(f"Error while closing: {e}")
            self.reader = None
            self.writer = None


