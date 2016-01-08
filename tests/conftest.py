import os.path
from pytest import fixture
from tempfile import TemporaryDirectory
from subprocess import Popen, PIPE, run
from time import sleep


class Configuration:
    def __init__(self, **opts):
        for k, v in opts.items():
            setattr(self, k, v)


class DisqueNode:

    def __init__(self, port, dir):
        self.port = port
        self.dir = dir
        self.proc = None
        self.socket = os.path.join(dir, 'disque.sock')

    def start(self):
        if not self.proc:
            cmd = ["disque-server",
                   "--port", str(self.port),
                   "--dir", self.dir,
                   "--unixsocket", self.socket,
                   "--unixsocketperm", "755"]
            self.proc = Popen(cmd, stdout=PIPE, stderr=PIPE)

        cmd = ['disque', '-p', str(self.port), 'info']
        while True:
            sleep(.01)
            if self.proc.poll():
                raise Exception('already stopped!', self.proc.stderr)
            resp = run(cmd, stdout=PIPE, stderr=PIPE)
            if not resp.returncode:
                break

    def stop(self):
        self.proc.kill()
        self.proc = None

    @property
    def configuration(self):
        return Configuration(port=self.port, dir=self.dir, socket=self.socket)


@fixture(scope='function')
def node(request):
    tmp_dir = TemporaryDirectory()
    node = DisqueNode(port=7711, dir=tmp_dir.name)
    node.start()

    def teardown():
        node.stop()
        tmp_dir.cleanup()
    request.addfinalizer(teardown)
    return node.configuration
