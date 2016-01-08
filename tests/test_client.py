import asyncio
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


@pytest.mark.asyncio
async def test_pause(node, event_loop):
    client = Disque(node.port, loop=event_loop)

    response = await client.pause('q', 'state')
    assert response == 'none'
    await client.addjob('q', 'foo')

    response = await client.pause('q', 'all')
    assert response == 'all'
    with pytest.raises(ConnectionError):
        await client.addjob('q', 'bar')

    response = await client.pause('q', 'out', 'in')
    assert response == 'all'
    with pytest.raises(ConnectionError):
        await client.addjob('q', 'baz')

    response = await client.pause('q', 'in')
    assert response == 'in'
    with pytest.raises(ConnectionError):
        await client.addjob('q', 'qux')


@pytest.mark.asyncio
async def test_show_job(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    job_id = await client.addjob('q', 'bar')
    response = await client.show(job_id)
    assert hasattr(response, 'id')
    assert hasattr(response, 'queue')
    assert hasattr(response, 'state')
    assert hasattr(response, 'repl')
    assert hasattr(response, 'ttl')
    assert hasattr(response, 'ctime')
    assert hasattr(response, 'delay')
    assert hasattr(response, 'retry')
    assert hasattr(response, 'nacks')
    assert hasattr(response, 'additional_deliveries')
    assert hasattr(response, 'nodes_delivered')
    assert hasattr(response, 'nodes_confirmed')
    assert hasattr(response, 'next_requeue_within')
    assert hasattr(response, 'next_awake_within')
    assert hasattr(response, 'body')
    assert response.id == job_id

    with pytest.raises(ConnectionError):
        await client.show('foobar')


@pytest.mark.asyncio
async def test_delete_job(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    job_id = await client.addjob('q', 'bar')
    response = await client.deljob(job_id)
    assert response == 1
    response = await client.deljob(job_id)
    assert response == 0


@pytest.mark.asyncio
async def test_enqueue(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    job_id = await client.addjob('q', 'foo')
    response = await client.dequeue(job_id)
    assert response == 1
    response = await client.dequeue(job_id)
    assert response == 0
    response = await client.enqueue(job_id)
    assert response == 1
    response = await client.enqueue(job_id)
    assert response == 0


@pytest.mark.asyncio
async def test_jscan(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    jobs = set()
    for i in range(0, 512):
        job_id = await client.addjob('q', i, 5000, replicate=1, retry=0)
        jobs.add(job_id)

    found_jobs, cursor = set(), 0
    while True:
        cursor, items = await client.jscan(cursor, busyloop=True, count=128)
        found_jobs.update(items)
        if not cursor:
            break
    assert found_jobs == jobs


@pytest.mark.asyncio
async def test_jscan_all(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    job_id = await client.addjob('q', 'j', 5000, replicate=1, retry=0)

    response = await client.jscan(busyloop=True, reply='all')
    assert len(response.items) == 1
    job = response.items[0]
    assert hasattr(job, 'id')
    assert hasattr(job, 'queue')
    assert hasattr(job, 'body')
    assert job.id == job_id


@pytest.mark.asyncio
async def test_qscan(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    queues = set()
    for i in range(0, 512):
        queue = 'queue-%s' % i
        queues.add(queue)
        await client.addjob(queue, 'job', 5000, replicate=1, retry=0)

    found_queues, cursor = set(), 0
    while True:
        cursor, items = await client.qscan(cursor, count=128)
        found_queues.update(items)
        if not cursor:
            break
    assert found_queues == queues


@pytest.mark.asyncio
async def test_close_connection(node, event_loop):
    client = Disque(node.port, loop=event_loop)
    await client.hello()
    client.close()
    with pytest.raises(RuntimeError):
        await client.hello()


@pytest.mark.asyncio
async def test_close_reconnection(node, event_loop):
    client = Disque(node.port, loop=event_loop, auto_reconnect=True)
    await client.hello()
    client.close()
    with pytest.raises(RuntimeError):
        await client.hello()


@pytest.mark.asyncio
async def test_close_autoreconnection(node, event_loop):

    server = Wrapper(5678, node.port)
    await server.start()
    client = Disque(server.port, loop=event_loop, auto_reconnect=True)
    await client.hello()
    server.close()

    # really really closed connection
    with pytest.raises(ConnectionRefusedError):
        await client.hello()

    # connection get back
    await server.start()
    await client.hello()

    # half-closed connection
    server.close()
    await server.start()
    await client.hello()


class Wrapper:

    def __init__(self, port, redirect_port, *, loop=None):
        self.redirect_port = redirect_port
        self.port = port
        self.loop = loop

    async def start(self):
        self.server = await asyncio.start_server(self.handle,
                                                 '127.0.0.1',
                                                 self.port,
                                                 loop=self.loop)
        sockets = await asyncio.open_connection('127.0.0.1',
                                                self.redirect_port,
                                                loop=self.loop)
        self.reader, self.writer = sockets

    def close(self):
        if self.writer:
            self.writer.close()
            self.writer = None
        if self.server:
            self.server.close()
            self.server = None
        self.reader = None

    async def handle(self, reader, writer):
        data = await reader.read(10000)
        self.writer.write(data)
        data = await self.reader.read(10000)
        writer.write(data)
        await writer.drain()
        writer.close()
