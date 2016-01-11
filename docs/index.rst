.. AIO Disque documentation master file, created by
   sphinx-quickstart on Thu Jan  7 12:14:19 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

AIO Disque
==========

AIO Disque is a modern client for Disque_ — an ongoing experiment to build a
distributed, in-memory, message broker — using Python coroutines and the
explicit async/await introduced in Python3.5.


Contents
--------

.. toctree::
   :maxdepth: 2

* :doc:`getting-started`
* :doc:`reference`


Installation
------------

AIO Disques requires Python 3.5. You can install it using ``pip``::

    % python -m pip install aiodisque


An example
----------

Here is how to send and receive jobs from a local Disque server:

.. code-block:: python

    from aiodisque import Disque
    client = Disque()
    job_id = await client.sendjob('my-queue', 'body')
    job = await client.getjob('my-queue')


Additional Features
-------------------

AIO Disque tends to be 100% compatible with the disque api document.
It provides additional python goodies for queues and results iteration.


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _Disque: https://github.com/antirez/disque
