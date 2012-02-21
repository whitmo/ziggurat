#@@ remove
from gevent import monkey
monkey.patch_all()

from gevent import wsgi
from gevent_zeromq import zmq
from geventutil import server as gserver
from pyramid.config import Configurator
from pyramid.decorator import reify
from pyramid.response import Response
from webob.dec import wsgify
from zig.utils import coro
import gevent
import json
import signal
import sys
import time

sys.setcheckinterval(10000000)


class ReqRep(object):
    #exiting = mw.CallbackExiting
    def __init__(self, service_name, answers=None):
        self.context = zmq.Context()
        self.serve_socket = None
        self._client = None
        self.name = service_name
        self.initialized = False
        self.server = None
        self.server_address = None
        self.answers = answers

    def _initialize(self):
        pass

    def initialize(self):
        self.server = self.server or gevent.spawn(self.listener, self.answers)
        gevent.sleep(0)
        self._initialize()
        self.initialized = True
       
    def exiting_callback(self):
        self.client_socket.send_json(dict(action='exiting', node=self.key))

    address_base = 'tcp://127.0.0.1'

    def server_bind(self, socket):
        self.server_address = "%s:%s"  \
                              %(self.address_base,
                                socket.bind_to_random_port(self.address_base,
                                                           min_port=9152,
                                                           max_port=65536,
                                                           max_tries=1000))
        return self.server_address

    def listener(self, answer_factory):
        """
        a server
        """
        socket = self.serve_socket = self.context.socket(zmq.REP)
        self.server_bind(socket)
        gevent.sleep(0.1)
        respond = answer_factory(socket.send_json)
        while True:
            message = socket.recv_json()
            respond(message)
            gevent.sleep(0.1)

    @coro
    def handler_sink(self, handler_factory):
        handle = handler_factory(self)
        while True:
            response = (yield) 
            handle(response)

    @coro
    def asker(self, address=None, callback=None):
        """
        make requests of a 0mq service at {address}
        """
        socket = self.client_socket = self.context.socket(zmq.REQ)
        socket.connect(address)
        while True:
            payload = (yield)
            if len(payload) == 2:
                payload, callback = payload
            socket.send_json(payload)
            resp = socket.recv_json()
            if not callback is None:
                callback((self, resp))

    @reify
    def handle_request(self):
        self._requested = self.handler_sink(self.requested_dispatch)
        return self._requested.send


class Node(ReqRep):
    """
    a node
    """
    def __init__(self, service_name, server_handlers=None, hub="tcp://localhost:5559"):
        self.hub_address = hub
        super(Node, self).__init__(service_name, server_handlers)
        
    def _initialize(self):
        self.req(dict(name=self.name, address=self.server_address))

    def responders(self, (handle, resp)):
        if 'status' in resp:
            self.status = resp['status']

        if 'pong' in resp:
            self.last_ping = time.time()
            gevent.spawn(self.req, dict(ping=True, name=self.service_name))
            gevent.sleep(0)

    def req(self, payload):
        self.request(payload)

    @reify
    def send_request(self):
        """
        make a request of el hubbo
        """
        self._client = self.asker(self.hub_address, self.handle_response)
        return self._client.send

    @reify
    def handle_response(self):
        self._responder = self.handler_sink(self.responders)
        return self._responder.send

                
class Hub(object):
    def __init__(self, service_name, address="tcp://localhost:5559"):
        self.address = address
        super(Hub, self).__init__(service_name, self.answer_to_node)
        self.nodes = {}

    def server_bind(self, socket):
        socket.bind(self.address)
        return self.address

    @reify
    def answer_to_node(self):
        self._requested = self.handler_sink(self.answer_to_node)
        return self._requested.send

    @coro
    def _answer_to_node(self, send):
        while True:
            request = (yield)
            if 'ping' in request:
                send(dict(pong=True))
            if 'register' in request:
                self.node[request['name']] = self.asker(self.address,
                                                        self.answers_to_hub).send
                send(dict(status='registered'))

    def answers_to_hub(self, payload):
        _, nodesays = payload
        json.dumps(payload, indent=3)


class ReqRepMW(object):
    def __init__(self, app, rr):
        self.rr = self.rr
        self.app = self.app
        
    @wsgify
    def __call__(self, request):
        if not self.rr.initialized:
            self.rr.initialize()
        request.zmq = self.rr
        return request.get_response(self.app)


# class NodeApp(dict):
#     rr_class = Node
#     mw_class = ReqRepMW
#     make_server = staticmethod(make_server)

#     def __init__(self, *args, **kw):
#         super(NodeApp).__init__(*args, **kw)

#     def index(self, _, request):
#         return Response(repr(self.__class__))

#     def configure(self):
#         config = Configurator()
#         config.add_view(self.index, context=self)
#         return config

#     def make_wsgi_app(self, config):
#         wsgiapp = config.make_wsgi_app()
#         rr = self.rr_class()
#         return self.mw_class(wsgiapp, rr)
        
#     @classmethod
#     def serve(cls, host, port, **kw):
#         app = cls(**kw)
#         config = app.configure()
#         wsgiapp = app.make_wsgi_app(config)
#         server = cls.make_server(host, port, wsgiapp)
#         server.serve_forever()


# class HubApp(NodeApp):
#     """
#     I'm a hub
#     """

def call(address):
    context = zmq.Context()
    client = context.socket(zmq.REQ)
    client.connect(address)
    client.send_json(dict(world='hello'))
    return client.recv_json()

def resp(send):
    @coro
    def af():
        while True:
            print (yield)['world']
            send(dict(status=200))
    return af().send



if __name__ == "__main__":
    pass
