import curio
from aiodisque.util import parse_address, encode_command
from .exceptions import ConnectionError, ProtocolError
from .bases import ConnectionBase, parser


__all__ = ['connect', 'Connection']


async def connect(address, *, closed_listeners=None):
    """Open a connection to Disque server.
    """
    address = parse_address(address, host='127.0.0.1', port=7711)

    try:
        if address.proto == 'tcp':
            host, port = address.address
            future = curio.open_connection(host=host, port=port)
        elif address.proto == 'unix':
            path = address.address
            future = curio.open_unix_connection(path=path)
        sock = await future
        reader, writer = sock.make_streams()
    except ConnectionRefusedError as error:
        raise error
    except Exception as error:
        raise ConnectionError() from error
    return Connection(reader, writer,
                      closed_listeners=closed_listeners)


class Connection(ConnectionBase):

    def __init__(self, reader, writer, *, closed_listeners=None):
        self._reader = reader
        self._writer = writer
        self.parser = parser()
        self._closed_listeners = closed_listeners or []

    async def send_command(self, *args):
        """Send command to server
        """
        message = encode_command(*args)

        await self._writer.write(message)
        data = await self._reader.read(65536)
        self.parser.feed(data)
        response = self.parser.gets()
        if isinstance(response, ProtocolError):
            self._closing = True
            self._loop.call_soon(self._do_close, response)
            self.parser = parser()
            raise response
        if isinstance(response, Exception):
            raise response
        return response

    def close(self):
        """Close connection."""
        raise NotImplementedError()

    @property
    def closed(self):
        """True if connection is closed."""
        raise NotImplementedError()
