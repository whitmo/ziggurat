import gevent
import logging

logger = logging.getLogger(__name__)


class Receiver(object):
    """
    for listening on a SUB or PULL socket
    """
    def __init__(self, recv, handler=None, wait=0.1):
        self.handler = self.default_handler
        if not self.handler is None:
            self.handler = handler
        self.recv = recv
        self.greenlet = None

    def sleep(self):
        gevent.sleep(self.wait)

    def default_handler(self, payload):
        logger.info(str(payload))

    def loop(self):
        while True:
            msg = self.recv()
            self.handler(msg)
            self.sleep()

    def run(self):
        self.greenlet = gevent.spawn(self.loop)


    
        
