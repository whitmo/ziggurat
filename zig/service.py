from gevent import monkey
monkey.patch_all()

from gservice.core import Service
from path import path


class GPasteDeployService(Service):
    """
    A paste.deploy configurable fixture for spinning up multiple
    services.
    """
    def __init__(self, global_config, **settings):
        self.ini = path(global_config['__file__'])
        self.here = self.ini.parent
        self.global_config = global_config
        self.settings = settings

    def load_services(self):
        #parse settings
        pass
    
    def __call__(self, app):
        # return server
        import pdb;pdb.set_trace()
        pass





