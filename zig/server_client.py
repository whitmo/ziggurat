from gevent_zeromq import zmq
import gevent
import zig


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

