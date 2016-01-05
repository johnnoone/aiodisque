AIO Disque
==========


Asyncio client form disque_.


Installation::

    python -m pip install -e .


Usage::

    from aiodisque import Disque
    client = Disque()
    job_id = await client.sendjob('queue', 'body')


.. _disque: https://github.com/antirez/disque
