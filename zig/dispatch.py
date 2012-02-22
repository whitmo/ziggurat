from .interfaces import IActionRegistry
from pyramid.decorator import reify
from zope.interface import implementer
import logging
import venusian


logger = logging.getLogger(__name__)


class action(object):
    #@@ add validation
    iface = IActionRegistry
    def __init__(self, name):
        self.name = name

    def register(self, scanner, name, wrapped):
        registry = scanner.config.registry
        registry.getUtility(self.iface).register(
            self.name, wrapped
            )

    def __call__(self, wrapped):
        venusian.attach(wrapped, self.register)
        return wrapped


class ActionConflictError(ValueError):
    """
    A error related to registering an action
    """

class NoActionError(ValueError):
    """
    No action found for the payload
    """


@implementer(IActionRegistry)
class ActionRegistry(dict):

    def __init__(self, registry, **kw):
        super(ActionRegistry, self).__init__(**kw) 
        self.registry = registry

    def register(self, name, callable_):
        if name in self:
            raise ActionConflictError("Confict! %s: %s vs. %s" %(name, callable_, self[name]))
        self[name] = callable_

    # divide into 'default' & 'not found'

    @reify
    def default(self):
        default = self.get('default')
        if default is not None:
            return default
        raise NoActionError('default')

    def dispatch(self, payload):
        action = payload.get('action', 'default')
        if action is None:
            raise NoActionError

        action = self.get(action, self.default)
        try:
            out = action(payload, self.registry)
        except Exception, e:
            logger.error("Action failed", exc_info=True)
            out = dict(status='fail', exception=repr(e))
        return out

    def __call__(self, send, payload):
        out = self.dispatch(payload)
        send(out)
        return out
