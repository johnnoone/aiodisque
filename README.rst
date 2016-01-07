AIO Disque
==========

Python3.5 & Asyncio client for disque_ message broker.


Installation
------------

aiodisque requires a running disque server.

::

    python -m pip install -e .


Getting started
---------------

Usage::

    from aiodisque import Disque
    client = Disque()
    job_id = await client.sendjob('queue', 'body')

API Reference
-------------

The `official Disque command documentation`_ does a great job of explaining
each command in detail. There are a few exceptions:

* each method are lowered
* async keywords are replaced by asap

In addition to the changes above, it implements some async sugar:

* iterators::

    async for jobs in client.client.getjob_iter('q', nohang=True):
        print(jobs)

    async for queue in client.qscan_iter(count=128):
        print(queue)

    async for job in client.jscan_iter(count=128):
        print(job)

* mimic an asyncio Queue::

    from aiodisque.queue import Queue
    queue = JobsQueue('queue', client)
    job_id = await queue.put('job')
    job = await queue.get()
    assert job.id == job_id

.. _disque: https://github.com/antirez/disque
.. _`official Disque command documentation`: https://github.com/antirez/disque#main-api
