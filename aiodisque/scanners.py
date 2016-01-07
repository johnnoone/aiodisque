from collections import deque
from collections.abc import AsyncIterator


class ScannerIterator(AsyncIterator):

    def __init__(self, func, func_args, func_kwargs):
        self.cursor = 0
        self.buffer = deque()
        self.state = 'waiting'
        self.func = func
        self.func_args = func_args
        self.func_kwargs = func_kwargs

    async def __aiter__(self):
        self.cursor = 0
        self.state == 'waiting'
        return self

    async def __anext__(self):
        if not self.buffer:
            await self.fetch_data()
        if self.buffer:
            return self.buffer.popleft()
        raise StopAsyncIteration()

    async def fetch_data(self):
        if self.state != 'finished':
            self.cursor, data = await self.func(self.cursor,
                                                *self.func_args,
                                                **self.func_kwargs)
            self.state = 'finished' if self.cursor == 0 else 'running'
            self.buffer.extend(data)


class JobsScanner(ScannerIterator):

    def __init__(self, client, *,
                 states=None, count=None, queue=None, reply=None):
        func = client.jscan
        func_args = states or []
        func_kwargs = {
            'count': count,
            'queue': queue,
            'reply': reply
        }
        super().__init__(func, func_args, func_kwargs)


class QueuesScanner(ScannerIterator):

    def __init__(self, client, *,
                 count=None, minlen=None, maxlen=None, import_rate=None):
        func = client.qscan
        func_args = []
        func_kwargs = {
            'count': count,
            'minlen': minlen,
            'maxlen': maxlen,
            'import_rate': import_rate
        }
        super().__init__(func, func_args, func_kwargs)
