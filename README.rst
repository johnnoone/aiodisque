AIO Disque
==========

Python3.5 & Asyncio client for Disque_ message broker.

Sources are available at https://lab.errorist.xyz/aio/aiodisque,
and mirrored at https://github.com/johnnoone/aiodisque.


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

``client`` accepts a tcp or unix address::

    client = Disque(address='127.0.0.1:7711')
    client = Disque(address=('127.0.0.1', 7711))
    client = Disque(address='/path/to/socket')


API Reference
-------------

The `official Disque command documentation`_ does a great job of explaining
each command in detail. There are a few exceptions:

* each method are lowered
* ``async`` keywords are replaced by asynchronous

In addition to the changes above, it implements some async sugar:

* Fancy async iterators::

    async for jobs in client.client.getjob_iter('q', nohang=True):
        print(jobs)

    async for queue in client.qscan_iter(count=128):
        print(queue)

    async for job in client.jscan_iter(count=128):
        print(job)

* There is also an experimentaton that try to mimic an asyncio.Queue::

    from aiodisque.queue import Queue
    queue = JobsQueue('queue', client)
    job_id = await queue.put('job')
    job = await queue.get()
    assert job.id == job_id

* client can reconnect automatically when a connection lost::

    from aiodisque import Disque
    client = Disque(auto_reconnect=True)
    await client.hello()
    # ... connection has been lost here...
    await client.hello()  # this not fails

For more details about the python implementation, you can consult the
`AIO Disque documentation`_.


TODO
----

* use state object instead of str for pause.
* more tests for qstat.
* handle -PAUSED errors and None queues (qstat).
* document pur python/asyncio feature.

.. _Disque: https://github.com/antirez/disque
.. _`official Disque command documentation`: https://github.com/antirez/disque#main-api
.. _`AIO Disque documentation`: http://aio.pages.errorist.xyz/aiodisque
