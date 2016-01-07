from collections.abc import AsyncIterator

__all__ = ['JobsIterator']


class JobsIterator(AsyncIterator):
    """Job async iterator

    Parameters:
        nohang (bool): ask the command to don't block even if there are
                       no jobs in all the specified queues
        timeout (int): in micro seconds
        count (int): number of jobs per calls
        withcounters (bool): Return the best-effort count of negative
                             acknowledges received by this job,
                             and the number of additional deliveries
                             performed for this job
        *queues: list of queue names, with one required
        padding (int): if count is set, it will pad results

    ``padding`` ensures that iterations will all have the same size.

    For example, this fails:

    >>> client = Disque()
    >>> await client.addjob('q', 'j1')
    >>> await client.addjob('q', 'j2')
    >>> jobs = JobsIterator(client, 'q', count=3, nohang=True)
    >>> try:
    >>>     await for j1, j2, j3 in jobs:
    >>>         assert isinstance(j1, Job)
    >>>         assert isinstance(j2, Job)
    >>>         assert j3 is None
    >>> except ValueError as error:
    >>>     print('It has been failed', error)

    But this one works:

    >>> client = Disque()
    >>> await client.addjob('q', 'j1')
    >>> await client.addjob('q', 'j2')
    >>> jobs = JobsIterator(client, 'q', count=3, nohang=True, padding=True)
    >>> await for j1, j2, j3 in jobs:
    >>>     assert isinstance(j1, Job)
    >>>     assert isinstance(j2, Job)
    >>>     assert j3 is None

    """

    def __init__(self, client, *queues, nohang=None, timeout=None,
                 count=None, withcounters=None, padding=None):
        """

        Parameters:
            nohang (bool): ask the command to don't block even if there are
                           no jobs in all the specified queues
            timeout (int): in micro seconds
            count (int): number of jobs per calls
            withcounters (bool): Return the best-effort count of negative
                                 acknowledges received by this job,
                                 and the number of additional deliveries
                                 performed for this job
            *queues: list of queue names, with one required
            padding (int): if count is set, it will pad results
        """
        self.client = client
        self.args = queues
        self.kwargs = {
            'nohang': nohang,
            'timeout': timeout,
            'count': count,
            'withcounters': withcounters
        }
        self.padding = padding and count

    async def __aiter__(self):
        return self

    async def __anext__(self):
        jobs = await self.get()
        if jobs:
            return jobs
        raise StopAsyncIteration()

    async def get(self):
        """Get fetch new jobs

        Returns:
            Returns a list of :class:`Job`.
            By default it will returns the exacts jobs found, but sometimes
            we need to garanty the same number of slots.
            For this case  filling ``padding`` and ``count`` values will
            fill results with ``None` slots.
        """
        jobs = await self.client.getjob(*self.args, **self.kwargs)
        if jobs and self.padding:
            return jobs + [None] * (self.padding - len(jobs))
        return jobs
