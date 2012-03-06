import geventutil.server
from pkg_resources import load_entry_point

def gpserve():
    load_entry_point('pyramid', 'console_scripts', 'pserve')()
