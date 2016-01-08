import asyncio
import hiredis
from .util import parse_address, encode_command

__all__ = ['Connection', 'ConnectionError']


def parser():
    return hiredis.Reader(protocolError=ProtocolError,
                          replyError=ConnectionError,
                          encoding='utf-8')


class ConnectionError(RuntimeError):
    pass


class ProtocolError(ConnectionError):
    pass


class Connection:

    def __init__(self, address, *, loop=None):
        self.address = parse_address(address, host='127.0.0.1', port=7711)
        self.loop = loop
        self.reader = None
        self.writer = None
        self.parser = parser()
        self.connected = False

    async def send_command(self, *args):
        await self.connect()
        message = encode_command(*args)

        self.writer.write(message)
        data = await self.reader.read(65536)
        self.parser.feed(data)

        response = self.parser.gets()
        if isinstance(response, ProtocolError):
            self.parser = parser()
            raise response
        if isinstance(response, Exception):
            raise response
        return response

    async def connect(self):
        if self.connected:
            return

        if self.address.proto == 'tcp':
            host, port = self.address.address
            future = asyncio.open_connection(host=host, port=port,
                                             loop=self.loop)
        elif self.address.proto == 'unix':
            path = self.address.address
            future = asyncio.open_unix_connection(path=path, loop=self.loop)
        reader, writer = await future
        self.reader = reader
        self.writer = writer
        self.connected = True
