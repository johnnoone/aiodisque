AIO Disque
==========


Asyncio client form disque_.


Installation::

    python -m pip install -e .


Usage::

    from aiodisque import Disque
    client = Disque()
    job_id = await client.sendjob('queue', 'body')

    async for queue in client.qscan_iterator(count=128):
        print(queue)

.. _disque: https://github.com/antirez/disque
