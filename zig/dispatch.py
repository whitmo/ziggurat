from .interfaces import IActionRegistry
from .interfaces import IReceptionRegistry
from functools import partial
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


class ErrorHandler(object):
    """
    A generic context manager for handling exits
    #@@ add 
    """
    def __init__(self, actions, send, payload):
        self.actions = actions
        self.send = send
        self.payload = payload

    def __enter__(self):
        logger.debug(self.payload)

    def handle_error(self, exc_type, exc_val, exc_tb):
        if self.actions.verbose > 1:
            logger.exception('BOOM')
        elif exc_val and self.actions.verbose == 1:
            logger.error()
        self.send(dict(status='fail', error=(repr(exc_type), repr(exc_val)), payload=self.payload))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.actions.postmortem and exc_val:
            import pdb; pdb.post_mortem(exc_tb)
        if exc_val:
            self.handle_error(exc_type, exc_val, exc_tb)



        

@implementer(IActionRegistry)
class ActionRegistry(dict):
    """
    """
    verbose = 2
    postmortem = True
    error_handler_class = ErrorHandler
    def __init__(self, registry, **kw):
        super(ActionRegistry, self).__init__(**kw) 
        self.registry = registry

    def register(self, name, callable_):
        if name in self:
            raise ActionConflictError("Confict! %s: %s vs. %s" %(name, callable_, self[name]))
        self[name] = callable_

    # divide into 'default' & 'not found'

    @reify
    def error_handler(self):
        return partial(self.error_handler_class, self)
        

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
        out = action(payload, self.registry)
        return out

    def __call__(self, send, payload):
        import pdb;pdb.set_trace()
        with self.error_handler(send, payload):
            out = self.dispatch(payload)
            send(out)
        return out


@implementer(IReceptionRegistry)
class ReceptionRegistry(ActionRegistry):
    """
    only receives, never gives.
    """
    def __call__(self, payload):
        out = self.dispatch(payload)
        return out
