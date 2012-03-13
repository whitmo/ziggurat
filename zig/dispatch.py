from .interfaces import IActionRegistry
from .interfaces import IReceptionRegistry
from contextlib import contextmanager
from functools import partial
from pyramid.decorator import reify
from zope.interface import implementer
import sys
import logging
import venusian
import traceback as tb

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
    """
    hot action
    """
    verbose = 2
    def __init__(self, registry, postmortem=False, **kw):
        super(ActionRegistry, self).__init__(**kw) 
        self.registry = registry
        self.postmortem = postmortem

    def handle_error(self, send, payload, (exc_type, exc_val, exc_tb)):
        if self.verbose > 1:
            logger.exception('BOOM')
        elif self.verbose == 1:
            logger.error()
            
        send(dict(status='fail', tb=tb.format_tb(exc_tb), error=(repr(exc_type), repr(exc_val))))

    @contextmanager
    def error_catcher(self, send, payload,  pm=False):
        try:
            yield
        except :
            exc_type, exc_val, exc_tb = sys.exc_info()
            if pm:
                import pdb; pdb.post_mortem(exc_tb)
            self.handle_error(send, payload, (exc_type, exc_val, exc_tb))        

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
        out = action(payload, self.registry)
        return out

    def __call__(self, send, payload):
        out = None
        with self.error_catcher(send, payload, pm=self.postmortem):
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
