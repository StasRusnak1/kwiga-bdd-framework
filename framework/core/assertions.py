def assert_true(condition: bool, message: str = "Assertion failed"):
    if not condition:
        raise AssertionError(message)

def assert_contains(container, item, message: str = None):
    if item not in container:
        raise AssertionError(message or f"{item!r} not found in {container!r}")
