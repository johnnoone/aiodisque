import pytest
from aiodisque import Disque
from aiodisque.iterators import JScanIterator, QScanIterator


@pytest.mark.asyncio
async def test_queues(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    queues = set()
    for i in range(0, 512):
        queue = 'queue-%s' % i
        queues.add(queue)
        await client.addjob(queue, 'job', 5000, replicate=1, retry=0)

    found_queues = set()
    it = client.qscan_iterator(count=128)
    async for queue in it:
        found_queues.add(queue)
    assert found_queues == queues
    assert isinstance(it, QScanIterator)


@pytest.mark.asyncio
async def test_jobs(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    jobs = set()
    for i in range(0, 512):
        job_id = await client.addjob('q', i, 5000, replicate=1, retry=0)
        jobs.add(job_id)

    found_jobs = set()
    it = client.jscan_iterator(count=128)
    async for queue in it:
        found_jobs.add(queue)
    assert found_jobs == jobs
    assert isinstance(it, JScanIterator)
