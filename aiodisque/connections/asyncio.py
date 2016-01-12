import asyncio
from aiodisque.util import parse_address, encode_command
from .exceptions import ConnectionError, ClosedConnectionError, ProtocolError
from .bases import ConnectionBase, parser

__all__ = ['connect', 'Connection']


async def connect(address, *, loop=None, closed_listeners=None):
    """Open a connection to Disque server.
    """
    address = parse_address(address, host='127.0.0.1', port=7711)

    try:
        if address.proto == 'tcp':
            host, port = address.address
            future = asyncio.open_connection(host=host, port=port, loop=loop)
        elif address.proto == 'unix':
            path = address.address
            future = asyncio.open_unix_connection(path=path, loop=loop)
        reader, writer = await future
    except ConnectionRefusedError as error:
        raise error
    except Exception as error:
        raise ConnectionError() from error
    return Connection(reader, writer,
                      loop=loop,
                      closed_listeners=closed_listeners)


class Connection(ConnectionBase):

    def __init__(self, reader, writer, *, loop=None, closed_listeners=None):
        self._loop = loop
        self._reader = reader
        self._writer = writer
        self.parser = parser()
        self._closed = False
        self._closing = None
        self._closed_listeners = closed_listeners or []

    async def send_command(self, *args):
        """Send command to server
        """
        if self.closed:
            raise ClosedConnectionError('closed connection')

        message = encode_command(*args)

        self._writer.write(message)
        data = await self._reader.read(65536)
        if self._reader.at_eof():
            self._closing = True
            self._loop.call_soon(self._do_close, None)
            raise ClosedConnectionError('Half closed connection')
        self.parser.feed(data)
        response = self.parser.gets()
        if isinstance(response, ProtocolError):
            self._closing = True
            self._loop.call_soon(self._do_close, response)
            self.parser = parser()
            raise response
        if isinstance(response, Exception):
            raise response

        if self._reader.at_eof():
            self._closing = True
            self._loop.call_soon(self._do_close, None)
        return response

    def close(self):
        """Close connection."""
        self._do_close(None)

    @property
    def closed(self):
        """True if connection is closed."""
        closed = self._closing or self._closed
        if not closed and self._reader and self._reader.at_eof():
            self._closing = closed = True
            self._loop.call_soon(self._do_close, None)
        return closed

    def _do_close(self, exc):
        if not self._closed:
            self._closed = True
            self._closing = False
            self._writer.transport.close()
            self._writer = None
            self._reader = None
            for listener in self._closed_listeners:
                listener()
