from gevent import monkey
monkey.patch_all()

import sys
from pkg_resources import load_entry_point

sys.setcheckinterval(10000000)

def gpserve():
    load_entry_point('pyramid', 'console_scripts', 'pserve')()
