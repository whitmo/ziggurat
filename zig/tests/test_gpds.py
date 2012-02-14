from  paste.deploy import loadapp
from  paste.deploy import loadserver
from path import path
import unittest


class TestGPDS(unittest.TestCase):
    def makeone(self, ini=path('.') / 'test_gpds.ini'):
        pass


    def test_load_ini(self):
        self.makeone()
