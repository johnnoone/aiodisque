import pytest
from aiodisque.connections.curio import connect


@pytest.mark.curio
async def test_curio(node, kernel):
    connection = await connect(node.port)
    response = await connection.send_command('HELLO')
    assert isinstance(response, list)
    assert len(response) == 3
