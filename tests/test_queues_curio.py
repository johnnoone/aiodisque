import pytest
from aiodisque import Disque
from aiodisque.connections.curio import connect as curio_connector
from aiodisque.queues import JobsQueue


@pytest.mark.curio
async def test_get_curio(node):
    client = Disque(node.port, connector=curio_connector)
    queue = JobsQueue('q', client)
    await client.addjob('q', 'job', 5000, replicate=1, retry=0)
    job = await queue.get()
    assert hasattr(job, 'id')
    assert hasattr(job, 'body')
    assert hasattr(job, 'body')
    assert hasattr(job, 'queue')
    assert not hasattr(job, 'nacks')
    assert not hasattr(job, 'additional_deliveries')


@pytest.mark.curio
async def test_get_nowait_curio(node):
    client = Disque(node.port, connector=curio_connector)
    queue = JobsQueue('q', client)

    with pytest.raises(NotImplementedError):
        queue.get_nowait()


@pytest.mark.curio
async def test_put_curio(node):
    client = Disque(node.port, connector=curio_connector)
    queue = JobsQueue('q', client)
    await queue.put('job')
    job = await client.getjob('q')
    assert hasattr(job, 'id')
    assert hasattr(job, 'body')
    assert hasattr(job, 'body')
    assert hasattr(job, 'queue')
    assert not hasattr(job, 'nacks')
    assert not hasattr(job, 'additional_deliveries')


@pytest.mark.curio
async def test_put_nowait_curio(node):
    client = Disque(node.port, connector=curio_connector)
    queue = JobsQueue('q', client)

    with pytest.raises(NotImplementedError):
        queue.put_nowait('job')
