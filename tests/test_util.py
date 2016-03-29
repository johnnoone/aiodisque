import pytest
from aiodisque.util import encode_command

def test_encode_command():
    data = encode_command('foo')
    assert data == b'*1\r\n$3\r\nfoo\r\n'

    data = encode_command(42)
    assert data == b'*1\r\n$2\r\n42\r\n'

    with pytest.raises(TypeError):
        encode_command(None)
