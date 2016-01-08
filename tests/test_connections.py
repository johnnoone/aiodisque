import pytest
from aiodisque import connect, Connection, ConnectionError
from unittest.mock import Mock


@pytest.mark.asyncio
async def test_tcp(node, event_loop):
    connection = await connect(node.port, loop=event_loop)
    response = await connection.send_command('HELLO')
    assert isinstance(response, list)
    assert len(response) == 3


@pytest.mark.asyncio
async def test_unix(node, event_loop):
    connection = await connect(node.socket, loop=event_loop)
    assert isinstance(connection, Connection)
    response = await connection.send_command('HELLO')
    assert isinstance(response, list)
    assert len(response) == 3


@pytest.mark.asyncio
async def test_tcp_recover(node, event_loop):
    connection = await connect(node.port, loop=event_loop)
    assert isinstance(connection, Connection)
    response = await connection.send_command('HELLO')
    assert isinstance(response, list)
    assert len(response) == 3


@pytest.mark.asyncio
async def test_closed(node, event_loop):
    connection = await connect(node.port, loop=event_loop)

    assert not connection.closed
    await connection.send_command('HELLO')

    connection.close()
    assert connection.closed
    with pytest.raises(ConnectionError):
        await connection.send_command('HELLO')


@pytest.mark.asyncio
async def test_close_callback(node, event_loop):

    spy = Mock()
    connection = await connect(node.port,
                               loop=event_loop,
                               closed_listeners=[spy])

    assert not spy.called
    assert not connection.closed
    connection.close()
    assert spy.called
    assert connection.closed
