import pytest
from aiodisque import Disque, ConnectionError


@pytest.mark.asyncio
async def test_hello(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    response = await client.hello()
    assert isinstance(response, dict)
    assert 'format' in response
    assert 'nodes' in response
    assert 'id' in response


@pytest.mark.asyncio
async def test_info(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    response = await client.info()
    assert isinstance(response, dict)
    assert 'registered_jobs' in response


@pytest.mark.asyncio
async def test_qstat_empty(node, event_loop):
    client = Disque(node.port, loop=event_loop)

    response = await client.qstat('foo')
    assert response is None

    response = await client.qlen('foo')
    assert response == 0


@pytest.mark.asyncio
async def test_qstat_notempty(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    await client.addjob('foo', 'bar')

    response = await client.qstat('foo')
    assert isinstance(response, dict)
    assert response['name'] == 'foo'

    response = await client.qlen('foo')
    assert response == 1


@pytest.mark.asyncio
async def test_job(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    job_id = await client.addjob('foo', 'bar')
    assert job_id.startswith('D-')

    response = await client.getjob('foo')
    assert isinstance(response, list)
    job = response[0]
    assert hasattr(job, 'id')
    assert hasattr(job, 'body')
    assert hasattr(job, 'body')
    assert hasattr(job, 'queue')
    assert not hasattr(job, 'nacks')
    assert not hasattr(job, 'additional_deliveries')
    assert job.id == job_id

    result = await client.ackjob(job)
    assert result == 1
    result = await client.ackjob(job)
    assert result == 0

    result = await client.nack(job)
    assert result == 0


@pytest.mark.asyncio
async def test_job_fastack(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    job_id = await client.addjob('foo', 'bar')
    assert job_id.startswith('D-')

    response = await client.getjob('foo')
    assert isinstance(response, list)
    job = response[0]
    assert hasattr(job, 'id')
    assert hasattr(job, 'body')
    assert hasattr(job, 'body')
    assert hasattr(job, 'queue')
    assert not hasattr(job, 'nacks')
    assert not hasattr(job, 'additional_deliveries')
    assert job.id == job_id

    result = await client.fastack(job)
    assert result == 1
    result = await client.fastack(job)
    assert result == 0

    result = await client.nack(job)
    assert result == 0


@pytest.mark.asyncio
async def test_job_working(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    job_id = await client.addjob('foo', 'bar')
    assert job_id.startswith('D-')

    response = await client.getjob('foo')
    assert isinstance(response, list)
    job = response[0]
    assert hasattr(job, 'id')
    assert hasattr(job, 'body')
    assert hasattr(job, 'body')
    assert hasattr(job, 'queue')
    assert not hasattr(job, 'nacks')
    assert not hasattr(job, 'additional_deliveries')
    assert job.id == job_id

    result = await client.working(job)
    assert result == 300
    result = await client.ackjob(job)
    assert result == 1
    with pytest.raises(ConnectionError):
        await client.working(job)

    result = await client.nack(job)
    assert result == 0
    with pytest.raises(ConnectionError):
        await client.working(job)


@pytest.mark.asyncio
async def test_job_withcounters(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    job_id = await client.addjob('foo', 'bar')
    assert job_id.startswith('D-')

    response = await client.getjob('foo', withcounters=True)
    assert isinstance(response, list)
    job = response[0]
    assert hasattr(job, 'id')
    assert hasattr(job, 'body')
    assert hasattr(job, 'queue')
    assert hasattr(job, 'nacks')
    assert hasattr(job, 'additional_deliveries')
    assert job.id == job_id

    result = await client.ackjob(job)
    assert result == 1
    result = await client.ackjob(job)
    assert result == 0


@pytest.mark.asyncio
async def test_qpeek_positive(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    await client.addjob('q', 'foo')
    await client.addjob('q', 'bar')
    await client.addjob('q', 'baz')
    response = await client.qpeek('q', 2)
    assert len(response) == 2
    assert response[0].body == 'foo'
    assert response[1].body == 'bar'


@pytest.mark.asyncio
async def test_qpeek_negative(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    await client.addjob('q', 'foo')
    await client.addjob('q', 'bar')
    await client.addjob('q', 'baz')
    response = await client.qpeek('q', -2)
    assert len(response) == 2
    assert response[0].body == 'baz'
    assert response[1].body == 'bar'
