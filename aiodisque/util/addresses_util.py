from functools import singledispatch

__all__ = ['Address', 'AddressError', 'parse_address']


class Address:

    def __init__(self, proto, address):
        self.proto = proto
        self.address = address

    def __eq__(self, other):
        if isinstance(other, Address):
            return self.proto == other.proto and self.address == other.address

    def __repr__(self):
        return '<Address(proto=%r, address=%r)>' % (self.proto, self.address)


class TCPAddress(Address):

    proto = 'tcp'

    def __init__(self, address):
        self.address = address


class UnixAddress(Address):

    proto = 'unix'

    def __init__(self, address):
        self.address = address


class AddressError(ValueError):

    def __init__(self, address):
        self.address = address
        super().__init__('do not know how to handle %r' % [address])


@singledispatch
def parse_address(address, **kwargs):
    raise AddressError(address)


@parse_address.register(Address)
def parse_addr_instance(address, **kwargs):
    return address


@parse_address.register(str)
def parse_addr_str(address, *, proto=None, host=None, port=None, **kwargs):
    if '://' in address:
        proto, _, address = address.partition('://')
    if ':' in address:
        proto = proto or 'tcp'
        a, _, b = address.partition(':')
        host = a or host
        port = b or port
        address = host, int(port)
    elif address.isdigit():
        proto = proto or 'tcp'
        port = int(address)
        address = host, int(port)
    elif address.startswith('/'):
        proto = proto or 'unix'
    else:
        proto = proto or 'tcp'
        host = address or host
        address = host, port
    if proto == 'unix':
        return UnixAddress(address=address)
    elif proto == 'tcp':
        return TCPAddress(address=address)


@parse_address.register(int)
def parse_addr_int(address, *, host=None, **kwargs):
    proto = 'tcp'
    address = host, address
    return Address(proto=proto, address=address)


@parse_address.register(list)
@parse_address.register(tuple)
def parse_addr_tuple(address, *, host=None, port=None, **kwargs):
    proto = 'tcp'
    try:
        a, b = address
        host = a or host
        port = b or port
        address = host, port
    except Exception as error:
        raise AddressError(address) from error
    return Address(proto=proto, address=address)
