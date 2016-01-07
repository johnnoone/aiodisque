from collections.abc import AsyncIterator


class JobsIterator(AsyncIterator):

    def __init__(self, client, *queues, nohang=None, timeout=None,
                 count=None, withcounters=None):
        self.client = client
        self.args = queues
        self.kwargs = {
            'nohang': nohang,
            'timeout': timeout,
            'count': count,
            'withcounters': withcounters
        }

    async def __aiter__(self):
        return self

    async def __anext__(self):
        jobs = await self.get()
        if jobs:
            return jobs
        raise StopAsyncIteration()

    async def get(self):
        return await self.client.getjob(*self.args, **self.kwargs)
