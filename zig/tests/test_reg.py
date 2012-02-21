import unittest 


class TestRegisterRoundTrip(unittest.TestCase):

    def makeone(self):
        from zig.config.register import scan
        return scan('zig.tests.simple_reg')

    def test_reg_roundtrip(self):
        reg = self.makeone()
        # test default value
        assert reg(dict(action='not_found')) is False
        assert reg(dict(action='dosomething')) is True
