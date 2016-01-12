import pytest
from aiodisque import Disque, Job
from aiodisque.connections.curio import connect as curio_connector
from aiodisque.iterators import JobsIterator


@pytest.mark.curio
async def test_queues(node):
    client = Disque(node.port, connector=curio_connector)
    expected = set()
    for i in range(0, 256):
        res = await client.addjob('q', 'job-%s' % i, 5000, replicate=1, retry=0)
        expected.add(res)

    it = client.getjob_iter('q', nohang=True)
    results = set()
    async for job in it:
        results.add(job.id)
    assert results == expected
    assert isinstance(it, JobsIterator)


@pytest.mark.curio
async def test_queues_count(node):
    client = Disque(node.port, connector=curio_connector)
    expected = set()
    for i in range(0, 256):
        res = await client.addjob('q', 'job-%s' % i, 5000, replicate=1, retry=0)
        expected.add(res)

    it = client.getjob_iter('q', nohang=True, count=2)
    results = set()
    async for jobs in it:
        results.update(job.id for job in jobs)
    assert results == expected
    assert isinstance(it, JobsIterator)


@pytest.mark.curio
async def test_queues_padding(node):
    client = Disque(node.port, connector=curio_connector)

    for i in range(0, 4):
        await client.addjob('q', 'job-%s' % i, 5000, replicate=1, retry=0)

    count = 0
    it = client.getjob_iter('q', nohang=True, count=3, padding=True)
    async for j1, j2, j3 in it:
        if count == 0:
            assert isinstance(j1, Job)
            assert isinstance(j2, Job)
            assert isinstance(j3, Job)
        elif count == 1:
            assert isinstance(j1, Job)
            assert j2 is None
            assert j3 is None
        else:
            break
        count += 1


@pytest.mark.curio
async def test_queues_padding_missing(node):
    client = Disque(node.port, connector=curio_connector)

    for i in range(0, 2):
        await client.addjob('q', 'job-%s' % i, 5000, replicate=1, retry=0)

    with pytest.raises(ValueError):
        it = client.getjob_iter('q', nohang=True, count=3)
        async for j1, j2, j3 in it:
            pass
