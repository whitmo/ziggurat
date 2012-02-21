from zope.interface import Interface
from zope.interface import Attribute


class IActionRegistry(Interface):
    dispatch_key = Attribute("Key to dispath actions upon")
    def __call__(payload):
        """
        executes an action based on payload contents
        """
