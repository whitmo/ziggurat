from .utils import coro
import zig
import zmq
import gevent
import logging

logger = logging.getLogger(__name__)

@coro
def ezpub(address="tcp://*:5556", context=None, sender='send', switch=True):
    context = context or zig.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(address)
    while True:
        try:
            message = (yield)
        except Exception as e:
            logger.info('Publisher exiting: %s', e)
            socket.close()
            raise
        send = getattr(socket, sender)
        send(message)
        if switch is True:
            gevent.sleep(0) 


def subscriber(address, opts=[''], context=None, recv='recv', handlers=[], wait=0.1):
    socket = context.socket(zmq.SUB)
    context = context or zig.Context()
    for opt in opts:
        socket.setsockopt(zmq.SUBSCRIBE, opt)
    socket.connect(address)
    while True:
        receiver = getattr(socket, 'recv')
        out = receiver()
        for handler in handlers:
            handler(out)
            gevent.sleep(0)
        gevent.sleep(wait)
        

# while True:
#     zipcode = random.randrange(1,100000)
#     temperature = random.randrange(1,215) - 80
#     relhumidity = random.randrange(1,50) + 10

#     socket.send("%d %d %d" % (zipcode, temperature, relhumidity))


#    pass
