import pytest
from aiodisque.util import parse_address, Address, AddressError

ok = [
    ('1.2.3.4', Address(proto='tcp', address=('1.2.3.4', 7711))),
    ('tcp://1.2.3.4', Address(proto='tcp', address=('1.2.3.4', 7711))),
    ('1237.0.0.1:', Address(proto='tcp', address=('1237.0.0.1', 7711))),
    (('1237.0.0.1', None), Address(proto='tcp', address=('1237.0.0.1', 7711))),
    (['1237.0.0.1', None], Address(proto='tcp', address=('1237.0.0.1', 7711))),
    (':', Address(proto='tcp', address=('127.0.0.1', 7711))),
    (':12', Address(proto='tcp', address=('127.0.0.1', 12))),
    ('12', Address(proto='tcp', address=('127.0.0.1', 12))),
    ('errorist.xyz', Address(proto='tcp', address=('errorist.xyz', 7711))),
    (12, Address(proto='tcp', address=('127.0.0.1', 12))),

    ('/tmp/disque.sock', Address(proto='unix', address='/tmp/disque.sock')),
    ('unix:///foo/bar.sock', Address(proto='unix', address='/foo/bar.sock')),

    (Address(proto='foo', address='bar'), Address(proto='foo', address='bar')),
]

fail = [('a',), ('a', 'b', 'c'), ['a'], ['a', 'b', 'c'], {}]


@pytest.mark.parametrize("input,expected", ok)
def test_parse_ok(input, expected):
    assert parse_address(input, host='127.0.0.1', port=7711) == expected


@pytest.mark.parametrize("input", fail)
def test_parse_fail(input):
    with pytest.raises(AddressError):
        parse_address(input)
