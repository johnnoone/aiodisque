Getting started
===============


Install from Pypi:

.. code-block:: shell

    $ python -m pip install aiodisque

Then start to play with it:

.. code-block:: python

    from aiodisque import Disque
    client = Disque()
    await for job1, job2 in client.getjob_iter('my-queue', nohang=True, count=2):
        print('-', job1.id, job1.body)
        print('-', job2.id, job2.body)

        await client.ackjob(job1)
        await client.ackjob(job2)

This library tries to follow the same naming conventions than the `original API`_.
Some changes must be noticed:

* commands are coroutines and thay names are lowered.
* ``async`` is a reserved word in Python, everyfields are renamed asynchronous

.. _`original API`: https://github.com/antirez/disque#main-api
