import pytest
from aiodisque import Disque
from aiodisque.iterators import JobsIterator


@pytest.mark.asyncio
async def test_queues(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    expected = set()
    for i in range(0, 256):
        job_id = await client.addjob('q', 'job-%s' % i, 5000, replicate=1, retry=0)
        expected.add(job_id)

    it = client.getjob_iter('q', nohang=True)
    results = set()
    async for jobs in it:
        results.update(job.id for job in jobs)
    assert results == expected
    assert isinstance(it, JobsIterator)
