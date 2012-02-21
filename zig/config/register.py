"""
A simple module scanner to build a dispatch system based on
"""
from pyramid.decorator import reify
import inspect
import sys
import venusian


class Action(object):
    attach = staticmethod(venusian.attach)

    def __init__(self, *args, **kwargs):
        self.arguments = (args, kwargs)
        
    def __call__(self, func):
        func._weez_action = self
        self.attach(func, self.add_handler)
        return func

    def add_handler(self, scanner, name, func):
        if scanner.registry is None:
            raise NoRegistryError()
        if name in scanner.registry:
            raise ActionConflictError("Confict! %s: %s vs. %s" %(name, func, scanner.registry[name]))
        scanner.registry[name] = func


class NoRegistryError(ValueError):
    """
    Scanner does not have an attached registry
    """

class ActionConflictError(ValueError):
    """
    A error related to registering an action
    """

class NoActionError(ValueError):
    """
    No action found for the payload
    """

def action(func):
    return Action()(func)


class Registry(dict):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @reify
    def default(self):
        default = self.get('default')
        if default is not None:
            return default
        raise NoActionError('default')

    def dispatch(self, payload, **kw):
        action = payload.get('action', None)
        if action is None:
            raise NoActionError
        action = self.get(action, self.default)
        return action(payload, **kw)

    def __call__(self, payload):
        return self.dispatch(payload, **self.kwargs)



class Scanner(venusian.Scanner):
    reg_class = Registry
    def invoke(self, name, ob):
        callback_map = getattr(ob, venusian.ATTACH_ATTR, None)
        if not callback_map is None:
            for gen in ((callback(self, name, ob) for callback in callbacks) \
                        for key, callbacks in callback_map.items()):
                [res for res in gen]
        
    def scan(self, package):
        """ Scan a Python package and any of its subpackages.  All
        top-level objects will be considered; those marked with
        venusian callback attributes will be processed.

        The ``package`` argument should be a reference to a Python
        package or module object.
        """
        for name, ob in inspect.getmembers(package):
            self.invoke(name, ob)

        if hasattr(package, '__path__') and getattr(self, 'walk', True) is True: # package, not module
            results = venusian.walk_packages(package.__path__, package.__name__+'.')
            for importer, modname, ispkg in results:
                __import__(modname)
                module = sys.modules[modname]
                for name, ob in inspect.getmembers(module, None):
                    self.invoke(name, ob)

    @classmethod
    def scan_module(cls, module_name, registry=None, walk=False):
        name = []
        if registry is None:
            registry = cls.reg_class()

        module_obj = module_name
        if not inspect.ismodule(module_name):
            mods = module_name.split('.')
            if len(mods) > 1:
                name = mods[:-1]        
        module_obj = __import__(module_name, globals(), locals(), name, -1)
        scan = cls(registry=registry, walk=walk).scan
        scan(module_obj)
        return registry

scan = Scanner.scan_module

    


# def handle_request(environ, start_response, dispatch=None, module=None, 
#                    request_class=Request, response_class=Response):
#     """
#     The main handler. Dispatches to the user's code.
#     """
#     request = request_class(environ)
#     try:
#         response = dispatch(request)
#         if response is None:
#             raise exc.HTTPNotFound()
#     except exc.WSGIHTTPException, e:
#         return e(environ, start_response)
#     except Exception, e:
#         #return exc.HTTPServerError('Server Error')
#         raise
    
#     if isinstance(response, basestring):
#         response = response_class(response)
    
#     return response(environ, start_response)


# def make_app(module=None, registry=None, walk=False):
#     """
#     Module name may be specified, otherwhise we stack jump and use the
#     one where this function is called.
    
#     If which_r is set to 'wz', wee will use the werkzeug request and
#     response objects
#     """
#     if module is None:
#         module = sys._getframe(1).f_globals['__name__']
#     registry = scan_module(module, registry, walk=walk)
#     return functools.partial(handle_request, module=module, request_class=Request, response_class=Response, dispatch=registry)


