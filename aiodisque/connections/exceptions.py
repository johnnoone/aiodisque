

class ConnectionError(RuntimeError):
    pass


class ClosedConnectionError(ConnectionError):
    pass


class ProtocolError(ConnectionError):
    pass
