from aiodisque.util import parse_address


def test_address():
    assert parse_address('1237.0.0.1:') == ('1237.0.0.1', None)
    assert parse_address(('1237.0.0.1', None)) == ('1237.0.0.1', None)
    assert parse_address(['1237.0.0.1', None]) == ('1237.0.0.1', None)
    assert parse_address(':') == ('localhost', None)
    assert parse_address(':12') == ('localhost', 12)
    assert parse_address('12') == ('localhost', 12)
    assert parse_address('errorist.xyz') == ('errorist.xyz', None)
    assert parse_address(12) == ('localhost', 12)
