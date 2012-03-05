from .interfaces import IZMQContext
from functools import partial
from gevent.threadpool import ThreadPool
from gevent_zeromq import zmq
from zope.interface import implementer
import atexit

class sock(object):
    def __init__(self, desc):
        self.desc = desc

    def make_sock(self, ctx=None, bind=None, connect=None, id=None):
        sock = ctx.socket(self.desc)
        if not id is None:
            sock.indentity = id
        assert not all((bind, connect)), ValueError("Cannot connect *and* bind")
        if not bind is None:
            sock.bind(bind)
        elif not connect is None:
            sock.connect(connect)
        return sock

    def __get__(self, ctx, objtype=None):
        return partial(self.make_sock, ctx=ctx)


@implementer(IZMQContext)
class ZMQContext(zmq.Context):
    """
    Extend the pyzmq context to include an interface declaration and
    some convenience.
    """
    router = sock(zmq.ROUTER)
    dealer = sock(zmq.DEALER)

    sub = sock(zmq.SUB)
    pub = sock(zmq.PUB)

    req = sock(zmq.REQ)
    rep = sock(zmq.REP)

    push = sock(zmq.PUSH)
    pull = sock(zmq.PULL)

    pair = sock(zmq.PAIR)

    def queue(self, front, back):
        tp = ThreadPool(1)
        front = self.router(bind=front)
        back = self.dealer(bind=back)
        result_obj = tp.spawn(zmq.device, zmq.QUEUE, front, back)
        return tp, result_obj


Context = ZMQContext


def includeme(config):
    """
    Pyramid extension bootystrap
    """
    ctx = Context()
    config.registry.registerUtility(ctx, IZMQContext)
    atexit.register(ctx.destroy)
    return config

def ctx_from_reg(reg):
    return reg.getUtility(IZMQContext)
