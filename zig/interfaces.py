from zope.interface import Interface
from zope.interface import Attribute


class IZMQContext(Interface):
    """
    a zmq context
    """


class IActionRegistry(Interface):
    dispatch_key = Attribute("Key to dispath actions upon")
    def __call__(send, payload):
        """
        executes an action based on payload contents, then sends the
        result via passed in callable send.
        """

class IReceptionRegistry(Interface):
    def __call__(payload):
        """
        executes an action based on payload contents
        """
