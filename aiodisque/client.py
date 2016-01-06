from .connections import Connection
from .iterators import JScanIterator, QScanIterator
from .util import grouper
from collections import namedtuple

__all__ = ['Disque', 'Job', 'Cursor']

Cursor = namedtuple('Cursor', 'cursor, items')


class Job:

    def __init__(self, queue, id, body, **kwargs):
        self.queue = queue
        self.id = id
        self.body = body
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<Job(queue=%r, id=%r, body=%r)>' % (self.queue,
                                                    self.id,
                                                    self.body)


def render_jobs(response):
    result = []
    for res in response:
        args = res[:3]
        ext = {k.replace('-', '_'): v for k, v in grouper(2, res[3:])}
        result.append(Job(*args, **ext))
    return result


class Disque:

    def __init__(self, address, *, loop=None):
        self.current_connection = Connection(address, loop=loop)

    async def addjob(self, queue, job, ms_timeout=0, *, replicate=None,
                     delay=None, retry=None, ttl=None,
                     maxlen=None, asap=False):
        """Adds a job to the specified queue

        The command returns the Job ID of the added job, assuming ASYNC is
        specified, or if the job was replicated correctly to the specified
        number of nodes. Otherwise an error is returned.

        Parameters:

            queue (str): name of the queue
            job (str): string representing the job. Max size is 4GB.
            ms_timeout (int): is the command timeout in milliseconds. If no
                              ASYNC is specified, and the replication level
                              specified is not reached in the specified number
                              of milliseconds, the command returns with an
                              error, and the node does a best-effort cleanup,
                              that is, it will try to delete copies of the job
                              across the cluster. However the job may still be
                              delivered later. Note that the actual timeout
                              resolution is 1/10 of second or worse with the
                              default server hz
            replicate (int): number of nodes the job should be replicated to
            delay (int): number of seconds that should elapse before the job
                         is queued by any server
            retry (int): in sec period after which, if no ACK is received, the
                         job is put again into the queue for delivery. If
                         RETRY is 0, the job has at-most-once delivery
                         semantics. The default retry time is 5 minutes, with
                         the exception of jobs having a TTL so small that 10%
                         of TTL is less than 5 minutes. In this case the
                         default RETRY is set to TTL/10 (with a minimum value
                         of 1 second)
            ttl (int): max job life in seconds. After this time, the job is
                       deleted even if it was not successfully delivered.
                       If not specified, the default TTL is one day
            maxlen (int): count specifies that if there are already count
                          messages queued for the specified queue name, the
                          message is refused and an error reported to the
                          client
            asap (bool): asks the server to let the command return ASAP and
                          replicate the job to other nodes in the background.
                          The job gets queued ASAP, while normally the job is
                          put into the queue only when the client gets a
                          positive reply.
        Returns:
            str: Job ID of the added job
        """
        params = ['ADDJOB', queue, job, ms_timeout]
        if replicate is not None:
            params.extend(('REPLICATE', replicate))
        if delay is not None:
            params.extend(('DELAY', delay))
        if retry is not None:
            params.extend(('RETRY', retry))
        if ttl is not None:
            params.extend(('TTL', ttl))
        if maxlen is not None:
            params.extend(('MAXLEN', maxlen))
        if asap is True:
            params.append('ASYNC')
        response = await self.execute_command(*params)
        return response

    async def getjob(self, *queues, nohang=None, timeout=None, count=None,
                     withcounters=None):
        """Return jobs available in one of the specified queues

        Return jobs available or NULL if the timeout is reached.

        If there are no jobs for the specified queues the command blocks, and
        messages are exchanged with other nodes, in order to move messages
        about these queues to this node, so that the client can be served.

        Parameters:
            nohang (bool): ask the command to don't block even if there are
                           no jobs in all the specified queues. This way the
                           caller can just check if there are available jobs
                           without blocking at all
            timeout (int): in micro seconds.
                           returns NULL if the timeout is reached
            count (int): a single job per call is returned unless a count
                         greater than 1 is specified
            withcounters (bool): Return the best-effort count of NACKs
                                 (negative acknowledges) received by this job,
                                 and the number of additional deliveries
                                 performed for this job
        """
        assert queues, 'At least one queue required'
        params = ['GETJOB']
        if nohang is True:
            params.append('NOHANG')
        if timeout is not None:
            params.extend(('TIMEOUT', timeout))
        if count is not None:
            params.extend(('COUNT', count))
        if withcounters is not None:
            params.append('WITHCOUNTERS')
        params.append('FROM')
        params.extend(queues)
        response = await self.execute_command(*params)
        if response is not None:
            return render_jobs(response)

    async def ackjob(self, *jobs):
        """Acknowledges the execution of one or more jobs via job IDs

        The node receiving the ACK will replicate it to multiple nodes and
        will try to garbage collect both the job and the ACKs from the
        cluster so that memory can be freed.

        A node receiving an ACKJOB command about a job ID it does not know,
        will create a special empty job, with the state set to "acknowledged",
        called a "dummy ACK". The dummy ACK is used in order to retain the
        acknowledge during a netsplit if the ACKJOB is send to a node that
        does not have a copy of the job. When the partition heals, a job
        garbage collection will be attempted.

        However since the job ID encodes information about the job being an
        "at most once" or an "at least once" job, the dummy ACK is only
        created for at least once jobs.

        Accepts Job instances and job_id

        Returns
            int: total of really acknowledged jobs
        """
        assert jobs, 'At least one job required'
        params = ['ACKJOB']
        params.extend(getattr(job, 'id', job) for job in jobs)
        response = await self.execute_command(*params)
        return response

    async def fastack(self, *jobs):
        """Performs a best effort cluster wide deletion of the specified job
        IDs.

        When the network is well connected and there are no node failures,
        this is equivalent to ACKJOB but much faster (less messages exchanged),
        however during failures it is more likely that fast acknowledges will
        result into multiple deliveries of the same messages.

        Accepts Job instances and job_id

        Returns:
            int: total of really acknowledged jobs
        """
        assert jobs, 'At least one job required'
        params = ['FASTACK']
        params.extend(getattr(job, 'id', job) for job in jobs)
        response = await self.execute_command(*params)
        return response

    async def working(self, job):
        """Claims to be still working with the specified job

        It asks Disque to postpone the next time it will deliver
        again the job. The next delivery is postponed for the job retry time,
        however the command works in a best effort way since there is no way
        to guarantee during failures that another node in a different network
        partition is performing a delivery of the same job.

        Returns:
            int: number of seconds you (likely) postponed the message
                 visiblity for other workers
        """
        params = ['WORKING']
        params.append(getattr(job, 'id', job))
        response = await self.execute_command(*params)
        return response

    async def nack(self, *jobs):
        """Tells Disque to put back the job in the queue ASAP.

        It is very similar to ENQUEUE but it increments the job nacks counter
        instead of the additional-deliveries counter. The command should be
        used when the worker was not able to process a message and wants the
        message to be put back into the queue in order to be processed again
        """
        assert jobs, 'At least one job required'
        params = ['NACK']
        params.extend(getattr(job, 'id', job) for job in jobs)
        response = await self.execute_command(*params)
        return response

    async def info(self):
        """Generic server information / stats
        """
        response = await self.execute_command('INFO')
        result = {}
        for line in response.splitlines():
            if not line:
                continue
            if line.startswith('#'):
                continue
            k, _, v = line.partition(':')
            result[k] = v
        return result

    async def hello(self):
        """Returns hello

        hello format version, this node ID, all the nodes IDs, IP addresses,
        ports, and priority (lower is better, means node more available).

        Clients should use this as an handshake command when connecting with
        a Disque node
        """
        response = await self.execute_command('HELLO')
        result = {k: v for k, v in zip(['format', 'id', 'nodes'], response)}
        nodes = []
        for node in grouper(4, result['nodes']):
            nodes.append({
                k: v for k, v in zip(['id', 'host', 'port', 'priority'], node)
            })
        result['nodes'] = nodes
        return result

    async def qlen(self, queue):
        """Return the length of the queue
        """
        response = await self.execute_command('QLEN', queue)
        return response

    async def qstat(self, queue):
        """Show information about a queue as an array of key value pairs

        This is an example of the output, however implementations should not
        rely on the order of the fields nor on the existance of the fields
        listed above. They may be (unlikely) removed or more can be (likely)
        added in the future.

        If a queue does not exist, NULL is returned. Note that queues are
        automatically evicted after some time if empty and without clients
        blocked waiting for jobs, even if there are active jobs for the queue.

        So the non existance of a queue does not mean there are not jobs in
        the node or in the whole cluster about this queue. The queue will be
        immediately created again when needed to serve requests.
        """
        response = await self.execute_command('QSTAT', queue)
        if response is not None:
            return {k: v for k, v in grouper(2, response)}
        return response

    async def qpeek(self, queue, count):
        """Return, without consuming from queue, count jobs

        If count is positive the specified number of jobs are returned from
        the oldest to the newest (in the same best-effort FIFO order as
        GETJOB). If count is negative the commands changes behavior and
        shows the count newest jobs, from the newest from the oldest.
        """
        response = await self.execute_command('QPEEK', queue, count)
        if response is not None:
            return render_jobs(response)

    async def enqueue(self, *jobs):
        """Queue jobs if not already queued
        """
        assert jobs, 'At least one job required'
        params = ['ENQUEUE']
        params.extend(getattr(job, 'id', job) for job in jobs)
        response = await self.execute_command(*params)
        return response

    async def dequeue(self, *jobs):
        """Remove the job from the queue
        """
        assert jobs, 'At least one job required'
        params = ['DEQUEUE']
        params.extend(getattr(job, 'id', job) for job in jobs)
        response = await self.execute_command(*params)
        return response

    async def deljob(self, *jobs):
        """Completely delete a job from a node

        Note that this is similar to FASTACK, but limited to a single node
        since no DELJOB cluster bus message is sent to other nodes
        """
        assert jobs, 'At least one job required'
        params = ['DELJOB']
        params.extend(getattr(job, 'id', job) for job in jobs)
        response = await self.execute_command(*params)
        return response

    async def show(self, job):
        """Describe the job
        """
        response = await self.execute_command('SHOW', getattr(job, 'id', job))
        params = {k.replace('-', '_'): v for k, v in grouper(2, response)}
        return Job(**params)

    async def qscan(self, cursor=None, *, count=None, busyloop=None,
                    minlen=None, maxlen=None, import_rate=None):
        """The command provides an interface to iterate all the existing
        queues in the local node, providing a cursor in the form of an
        integer that is passed to the next command invocation. During the
        first call cursor must be 0, in the next calls the cursor returned
        in the previous call is used in the next. The iterator guarantees
        to return all the elements but may return duplicated elements.

        Parameters:

            count (int): An hit about how much work to do per iteration
            busyloop (bool): Block and return all the elements in a busy loop
            minlen (int): Don't return elements with less than
                          count jobs queued
            maxlen (int): Don't return elements with more than
                          count jobs queued
            import_rate <rate>: Only return elements with an job import rate
                                (from other nodes) >= rate

        Returns:
            Cursor
        """
        params = ['qscan']
        if cursor is not None:
            params.append(cursor)
        if count is not None:
            params.extend(('COUNT', count))
        if busyloop is True:
            params.append('BUSYLOOP')
        if minlen is not None:
            params.extend(('MINLEN', minlen))
        if maxlen is not None:
            params.extend(('MAXLEN', maxlen))
        if import_rate is not None:
            params.extend(('IMPORTRATE ', import_rate))
        cursor, items = await self.execute_command(*params)
        return Cursor(int(cursor), items)

    def qscan_iterator(self, *, count=None,
                       minlen=None, maxlen=None, import_rate=None):
        return QScanIterator(self, count=count, minlen=minlen,
                             maxlen=maxlen, import_rate=import_rate)

    def jscan_iterator(self, *states, count=None, queue=None, reply=None):
        return JScanIterator(self, states=states, count=count,
                             queue=queue, reply=reply)

    async def jscan(self, cursor=None, *states, count=None, busyloop=None,
                    queue=None, reply=None):
        """The command provides an interface to iterate all the existing
        queues in the local node, providing a cursor in the form of an
        integer that is passed to the next command invocation. During the
        first call cursor must be 0, in the next calls the cursor returned
        in the previous call is used in the next. The iterator guarantees
        to return all the elements but may return duplicated elements.

        Parameters:

            count (int): An hit about how much work to do per iteration
            busyloop (bool): Block and return all the elements in a busy loop
            queue (str): Return only jobs in the specified queue
            states (str): Return jobs in the specified state. Can be used
                          multiple times for a logic OR
            reply (str): Job reply type. Type can be all or id. Default is to
                         report just the job ID. If all is specified the full
                         job state is returned like for the SHOW command

        Returns:
            Cursor
        """
        params = ['jscan']
        if cursor is not None:
            params.append(cursor)
        if count is not None:
            params.extend(('COUNT', count))
        if busyloop is True:
            params.append('BUSYLOOP')
        if queue is not None:
            params.extend(('QUEUE', queue))
        for state in states:
            params.extend(('STATE', state))
        if reply is not None:
            params.extend(('REPLY', reply))
        print(params)
        cursor, items = await self.execute_command(*params)
        if reply == 'all':
            result = []
            for item in items:
                params = {k.replace('-', '_'): v for k, v in grouper(2, item)}
                result.append(Job(**params))
            items = result

        return Cursor(int(cursor), items)

    async def pause(self, queue, *options):
        """Control the paused state of a queue

        possibly broadcasting the command to other nodes in the cluster.
        Disque queues can be paused in both directions, input and output or
        both. Pausing a queue makes it not available for input or output
        operations
        """
        assert options, 'at least one option required'
        response = await self.execute_command('PAUSE', queue, *options)
        return response

    async def execute_command(self, *args):
        return await self.current_connection.send_command(*args)
