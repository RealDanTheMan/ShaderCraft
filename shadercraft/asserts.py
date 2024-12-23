

def assertRef(ref, msg: str = None) -> None:
    """Raises assert exception if ref is None"""
    if ref is None:
        raise AssertionError(msg or "Assert failed! Reference is None")


def assertTrue(expr, msg: str = None) -> None:
    """Raises assert exception if expression is not True"""
    if not expr:
        raise AssertionError(msg or "Assert failed! Reference is None")


def assertFalse(expr, msg: str = None) -> None:
    """Raises exception if expression is not False"""
    if expr:
        raise AssertionError(msg or "Assert failed! Expression is true")
