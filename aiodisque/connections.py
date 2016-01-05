import asyncio
import hiredis
import logging
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
        self.address = parse_address(address, port=7711)
        self.loop = loop
        self.reader = None
        self.writer = None
        self.parser = parser()
        self.connected = False

    async def send_command(self, *args):
        await self.connect()
        message = encode_command(*args)
        logging.debug("REQ", message)

        self.writer.write(message)
        data = await self.reader.read(65536)
        self.parser.feed(data)
        logging.debug("RES", data)

        response = self.parser.gets()
        if isinstance(response, ProtocolError):
            self.parser = parser()
            raise response
        if isinstance(response, Exception):
            raise response
        return response

    async def connect(self):
        if not self.connected:
            reader, writer = await asyncio.open_connection(*self.address,
                                                           loop=self.loop)
            self.reader = reader
            self.writer = writer
            self.connected = True
