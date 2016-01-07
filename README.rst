AIO Disque
==========


Python3.5 & Asyncio client for disque_.


Installation::

    python -m pip install -e .


Usage::

    from aiodisque import Disque
    client = Disque()
    job_id = await client.sendjob('queue', 'body')

Asyncio iterators::

    async for queue in client.qscan_iterator(count=128):
        print(queue)

Mimic an asyncio Queue::

    from aiodisque.queue import Queue
    queue = JobsQueue('queue', client)
    job_id = await queue.put('job')
    job = await queue.get()
    assert job.id == job_id

.. _disque: https://github.com/antirez/disque
