from gevent.threadpool import ThreadPool
from gevent_zeromq import zmq
from gevent.coros import RLock
from contextlib import closing
import gevent
import zig


class RepServer(object):
    """
    aka Papa
    """
    wait = 0.1
    def __init__(self, handler, address=None, address_base='tcp://*',
                 context=None, serializer=None, bind=True, identity=None):
        self.context = context or zig.Context()
        self.handler = handler
        self.address = address
        self.address_base = address_base
        self.greenlet = None
        self.socket = self.context.rep()

        if not identity is None:
            self.socket.identity = identity

        self.bind = bind
        if self.bind is True:
            self.server_bind()
        else:
            self.socket.connect(self.address)
        
        self.recv = self.socket.recv
        self.send = self.socket.send
        if not serializer is None:
            self.recv = getattr(self.socket, "recv_%s" %serializer)
            self.send = getattr(self.socket, "send_%s" %serializer)

    @property
    def identity(self):
        return self.socket.identity

    def server_bind(self):
        if not self.address is None:
            self.socket.bind(self.address)
            return self.address

        self.address = "%s:%s"  \
                              %(self.address_base,
                                self.socket.bind_to_random_port(self.address_base,
                                                                min_port=9152,
                                                                max_port=65536,
                                                                max_tries=1000))
        return self.address

    def loop(self):
        """
        a server loop
        """
        gevent.sleep(self.wait)
        while True:
            message = self.recv() # may need to poll to avoid blocking
            self.handler(self.send, message)
            gevent.sleep(self.wait)

    def run(self):
        self.greenlet = gevent.spawn(self.loop)
        #gevent.sleep(0)
        return self.greenlet


class SimpleRRClient(object):
    
    def __init__(self, address, context=None, bind=False):
        ctx = self.context = context or zig.Context()
        self.socket = ctx.req()
        if bind is True:
            self.socket.bind(address)
        else:
            self.socket.connect(address)
        self.lock = RLock()

    def request(self, payload):
        assert 'action' in payload, "Must send an action to remote server"
        self.socket.send_json(payload)
        return self.socket.recv_json()

    def send(self, payload):
        with self.lock:
            return self.request(payload)


class endpoint(object):
    """
    Represents an address that one may make non-lingering
    `requests` on a remote address
    """
    def __init__(self, address, ctx=None, timeout=3*1000):
        self.ctx = self.context = ctx or zig.CTX()
        self.address = address
        self.timeout = timeout
        self.poll = zmq.Poller()

    def _recv_reply(self, sock):
        return sock.recv()

    def request(self, payload, timeout=None):
        client = self.ctx.req()
        with closing(client):
            client.connect(self.address.replace('*', '0.0.0.0'))
            client.linger = 0
            self.poll.register(client)
            timeout = timeout or self.timeout
            socks = dict(self.poll.poll(timeout))
            if socks.get(client) == zmq.POLLIN:
                reply = self._recv_reply(client)
            else:
                reply = None
            self.poll.unregister(client)
        return reply


class json_endpoint(endpoint):
    #@@ add validation ??
    def _recv_reply(self, sock):
        return sock.recv_json()    


def try_request(ctx, endpoint, request, timeout=3*1000):
    """
    from zguide
    """
    client = ctx.req()
    client.setsockopt(zmq.LINGER, 0)  # Terminate early
    client.connect(endpoint)
    client.send(request)
    poll = zmq.Poller()
    poll.register(client, zmq.POLLIN)
    socks = dict(poll.poll(timeout))
    if socks.get(client) == zmq.POLLIN:
        reply = client.recv_multipart()
    else:
        reply = None
    poll.unregister(client)
    client.close()
    return reply


def spawn_queue(front, back):
    tp = ThreadPool(1)
    result_obj = tp.spawn(zmq.device, zmq.QUEUE, front, back)
    return tp, result_obj



