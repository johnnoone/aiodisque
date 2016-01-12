import hiredis
from .exceptions import ConnectionError, ProtocolError


def parser():
    return hiredis.Reader(protocolError=ProtocolError,
                          replyError=ConnectionError,
                          encoding='utf-8')


class ConnectionBase:

    async def send_command(self, *args):
        """Send command to server
        """
        raise NotImplementedError()

    def close(self):
        """Close connection."""
        raise NotImplementedError()

    @property
    def closed(self):
        """True if connection is closed."""
        raise NotImplementedError()
