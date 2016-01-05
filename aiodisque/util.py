from itertools import zip_longest

__all__ = ['parse_address', 'encode_command']


def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def parse_address(address, *, host=None, port=None):
    host, port = host or 'localhost', port
    if isinstance(address, (list, tuple)):
        host, port = address
    if isinstance(address, int):
        port = address
    elif isinstance(address, str):
        if ':' in address:
            a, _, b = address.partition(':')
            host = a or host
            port = b or port
        elif address.isdigit():
            port = int(address)
        else:
            host = address or host
    return host, int(port) if port else None


_converters = {
    bytes: lambda val: val,
    bytearray: lambda val: val,
    str: lambda val: val.encode('utf-8'),
    int: lambda val: str(val).encode('utf-8'),
    float: lambda val: str(val).encode('utf-8'),
}


def _bytes_len(sized):
    return str(len(sized)).encode('utf-8')


def encode_command(*args):
    """Encodes arguments into redis bulk-strings array.
    Raises TypeError if any of args not of bytes, str, int or float type.
    """
    buf = bytearray()

    def add(data):
        return buf.extend(data + b'\r\n')

    add(b'*' + _bytes_len(args))
    for arg in args:
        if type(arg) in _converters:
            barg = _converters[type(arg)](arg)
            add(b'$' + _bytes_len(barg))
            add(barg)
            continue
        raise TypeError("Argument {!r} expected to be of bytes,"
                        " str, int or float type".format(arg))
    return buf
