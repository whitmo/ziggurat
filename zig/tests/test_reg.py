from mock import Mock
import unittest 


def dummy():
    pass


class TestActionDecorator(unittest.TestCase):
    """
    
    """
    def makeone(self, name):
        from zig.dispatch import action
        return action(name)

    def test_action_decorator(self):
        act = self.makeone('decorated')
        decorated = act(dummy)
        assert dummy == decorated
        assert None in dummy.__venusian_callbacks__
        cbs = dummy.__venusian_callbacks__[None]
        assert len(cbs) == 1
        assert cbs[0] == act.register

    def test_register(self):
        act = self.makeone('decorated')
        decorated = act(dummy)
        scanner = Mock()
        utility = Mock()
        utility.register = Mock()
        gu = scanner.config.registry.getUtility = Mock(return_value=utility)
        act.register(scanner, 'hey', decorated)
        assert gu.called
        assert utility.register.call_args[0] == ('decorated', dummy)

