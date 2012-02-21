from functools import partial
from gevent_zeromq import zmq
from zig.config.register import scan
from zig.utils import coro
import gevent
import zig


# class RRClient(object):
#     def __init__(self, address, callback=None, context=None):
#         self.context = context or zig.Context()
#         self.address = address
#         self.callback = callback
#         self.coro = None

#     @coro
#     def asker(self):
#         """
#         make requests of a 0mq service at {address}
#         """
#         socket = self.client_socket = self.context.socket(zmq.REQ)
#         socket.connect(self.address)
#         callback = None
#         while True:
#             payload = (yield)
#             if len(payload) == 2:
#                 payload, callback = payload
#             callback = callback or self.callback
#             socket.send_json(payload)
#             resp = socket.recv_json()
#             if not callback is None:
#                 callback((self, resp))

#     def send(self, payload, callback=None, retvalue=False):
#         if self.coro is None:
#             self.coro = self.asker()
#         if callback is None:
#             return self.coro.send((payload,))
#         return self.coro.send((payload, callback))


class ServerHandler(object):
    scan = staticmethod(scan)

    def __init__(self, server, dispatcher=None, registry=None):
        self.server = server
        self.dispatcher = dispatcher
        self.registry = registry

    def __call__(self, payload):
        out = self.dispatcher(payload, self.registry)
        self.server.socket.send_json(out)

    @classmethod
    def from_spec(cls, spec, registry):
        dispatcher = cls.scan(spec)
        return partial(cls, dispatcher=dispatcher, registry=registry)


class RepServer(object):
    wait = 0.1
    def __init__(self, handler, address=None, context=None):
        self.context = context or zig.Context()
        self.handler = handler
        self.address = address
        self.greenlet = None

    def server_bind(self, socket):
        if not self.address is None:
            socket.bind(self.address)
            return self.address
        
        self.address = "%s:%s"  \
                              %(self.address_base,
                                socket.bind_to_random_port(self.address_base,
                                                           min_port=9152,
                                                           max_port=65536,
                                                           max_tries=1000))
        return self.address
    
    def loop(self):
        """
        a server loop
        """
        socket = self.serve_socket = self.context.socket(zmq.REP)
        self.server_bind(socket)
        gevent.sleep(self.wait)
        while True:
            message = socket.recv_json()
            self.handler(socket.send_json, message)
            gevent.sleep(self.wait)

    def run(self):
        self.greenlet = gevent.spawn(self.loop)
        gevent.sleep(0)
        return self.greenlet


class SimpleRRClient(object):
    
    def __init__(self, address, context=None):
        self.context = context or zig.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(address)

    def send(self, payload):
        assert 'action' in payload, "Must send an action to remote server"
        self.socket.send_json(payload)
        return self.socket.recv_json()

