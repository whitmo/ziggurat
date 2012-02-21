from .interfaces import IZMQContext
from gevent_zeromq import zmq
from zope.interface import implementer

@implementer(IZMQContext)
class ZMQContext(zmq.Context):
    """
    So we can register it properly 
    """

Context = ZMQContext


def includeme(config):
    """
    Pyramid extension bootystrap
    """
    config.registry.registerUtility(Context(), IZMQContext)
    return config
