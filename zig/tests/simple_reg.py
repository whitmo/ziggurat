from zig.config.register import action

@action
def dosomething(payload):
    return True


@action
def default(payload):
    return False
