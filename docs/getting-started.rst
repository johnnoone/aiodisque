AIODisque Getting started
=========================


Install from Pypi:

.. code-block:: shell

    $ python -m pip install aiodisque

Then start to play with it:

.. code-block:: python

    from aiodisque import Disque
    client = Disque()
    jobs = client.getjob_iter('my-queue', nohang=True, count=2, padding=True)
    await for job1, job2 in jobs:
        print('-', job1.id, job1.body)
        print('-', job2.id, job2.body)

        await client.ackjob(job1)
        await client.ackjob(job2)

This library tries to follow the same naming conventions than the `original API`_.
Some changes must be noticed:

* commands are coroutines and thay names are lowered.
* ``async`` is a reserved word in Python, everyfields are renamed asynchronous


Event loops
-----------

This client works well with asyncio_, it is the default.

It also have a experimental implementation with curio_.
For using it, install the dependencies:

.. code-block:: shell

    $ python -m pip install aiodisque[curio]

And then hack with it:

.. code-block:: python

    from aiodisque import Disque
    from aiodisque.connections.curio import connect as curio_connector

    client = Disque(connector=curio_connector)
    await client.addjob('q', 'job')


Other goodies
-------------

:meth:`Disque.getjob` returns a single job by default. but it will return a
list if ``count`` is set:

.. code-block:: python

    from aiodisque import Disque
    client = Disque()

    # get a job instance
    await client.addjob('my-queue', 'job-1')
    job = await client.getjob('my-queue')

    # get a list of job instances
    await client.addjob('my-queue', 'job-2')
    jobs = await client.getjob('my-queue', count=1)

``padding`` with ``count`` ensure that iteration will returns the same number
of slots:

.. code-block:: python

    from aiodisque import Disque
    client = Disque()
    await client.addjob('my-queue', 'job-1')
    jobs = client.getjob_iter('my-queue', nohang=True, count=2, padding=True)
    await for job1, job2 in jobs:
        print('- job1:', job1.id, job1.body)
        print('- job2 is null:', job2 is None)

``auto_reconnect`` tries to handle half-closed connection, lost and back
connection...

.. code-block:: python

    from aiodisque import Disque
    client = Disque(auto_reconnect=True)


.. _`original API`: https://github.com/antirez/disque#main-api
.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _curio: http://curio.readthedocs.org
