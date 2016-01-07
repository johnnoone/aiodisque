import asyncio

__all__ = ['JobsQueue']


class JobsQueue:

    class Empty(Exception):
        """
        Exception raised when non-blocking :meth:`~EventsQueue.get`
        is called on a :class:`JobsQueue` object which is empty.
        """

    class Full(Exception):
        """
        Exception raised when :meth:`~EventsQueue.put` is called on a
        :class:`JobsQueue` object which is full.
        """

    def __init__(self, queue, client, *, maxsize=0, loop=None):
        """Constructor for a FIFO queue

        maxsize is an integer that sets the upperbound limit on the number of
        items that can be placed in the queue. Insertion will block once this
        size has been reached, until queue items are consumed. If maxsize is
        less than or equal to zero, the queue size is infinite
        """
        self.name = queue
        self.client = client
        self.maxsize = maxsize
        self.loop = loop or asyncio.get_event_loop()

    def empty(self):
        """Return True if the queue is empty, False otherwise
        """
        raise NotImplementedError

    def full(self):
        """Return True if there are maxsize items in the queue
        """
        raise NotImplementedError

    async def get(self, withcounters=None):
        """Remove and return an item from the queue

        If queue is empty, wait until an item is available.
        See also The empty() method.
        """
        jobs = await self.client.getjob(self.name, nohang=False,
                                        withcounters=None)
        return jobs.pop()

    def get_nowait(self, withcounters=None):
        """Remove and return an item from the queue

        Return an item if one is immediately available, else raise QueueEmpty
        """
        raise NotImplementedError

    async def join(self):
        """Block until all items in the queue have been gotten and processed.

        The count of unfinished tasks goes up whenever an item is added to
        the queue. The count goes down whenever a consumer thread calls
        task_done() to indicate that the item was retrieved and all work on it
        is complete. When the count of unfinished tasks drops to zero, join()
        unblocks.
        """
        raise NotImplementedError

    async def put(self, job, *, ms_timeout=0, replicate=None,
                  delay=None, retry=None, ttl=None):
        """Put an item into the queue.

        If the queue is full, wait until a free slot is available before
        adding item
        """
        job = getattr(job, 'body', job)
        response = await self.client.addjob(self.name, job, ms_timeout=0,
                                            replicate=None, delay=None,
                                            retry=None, ttl=None, asap=False,
                                            maxlen=self.maxsize or None)
        return response

    def put_nowait(self, job, *, ms_timeout=0, replicate=None,
                   delay=None, retry=None, ttl=None, maxlen=None):
        """Put an item into the queue without blocking.

        If no free slot is immediately available, raise QueueFull.
        """
        raise NotImplementedError

    def qsize(self):
        """Number of items in the queue
        """
        raise NotImplementedError

    def task_done(self):
        """Indicate that a formerly enqueued task is complete

        Used by queue consumers. For each get() used to fetch a task, a
        subsequent call to task_done() tells the queue that the processing
        on the task is complete.

        If a join() is currently blocking, it will resume when all items have
        been processed (meaning that a task_done() call was received for every
        item that had been put() into the queue).

        Raises ValueError if called more times than there were items placed in
        the queue.
        """
        raise NotImplementedError
