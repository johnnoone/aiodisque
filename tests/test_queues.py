import pytest
from aiodisque import Disque
from aiodisque.queues import JobsQueue


@pytest.mark.asyncio
async def test_get(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    queue = JobsQueue('q', client, loop=event_loop)
    await client.addjob('q', 'job', 5000, replicate=1, retry=0)
    job = await queue.get()
    assert hasattr(job, 'id')
    assert hasattr(job, 'body')
    assert hasattr(job, 'body')
    assert hasattr(job, 'queue')
    assert not hasattr(job, 'nacks')
    assert not hasattr(job, 'additional_deliveries')


@pytest.mark.asyncio
async def test_get_nowait(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    queue = JobsQueue('q', client, loop=event_loop)

    with pytest.raises(NotImplementedError):
        queue.get_nowait()


@pytest.mark.asyncio
async def test_put(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    queue = JobsQueue('q', client, loop=event_loop)
    job_id = await queue.put('job')
    response = await client.getjob('q')
    assert len(response) == 1
    job = response[0]
    assert hasattr(job, 'id')
    assert hasattr(job, 'body')
    assert hasattr(job, 'body')
    assert hasattr(job, 'queue')
    assert not hasattr(job, 'nacks')
    assert not hasattr(job, 'additional_deliveries')


@pytest.mark.asyncio
async def test_put_nowait(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    queue = JobsQueue('q', client, loop=event_loop)

    with pytest.raises(NotImplementedError):
        queue.put_nowait('job')
