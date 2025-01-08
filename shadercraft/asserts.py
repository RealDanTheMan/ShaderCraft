

def assertRef(ref, msg: str = None) -> None:
    """Raises assert exception if ref is None"""
    if ref is None:
        raise AssertionError(msg or "Assert failed! Reference is None")


def assertType(val, val_type: type, msg: str = None) -> None:
    """Raises assert exception if given value is not of given type"""
    if not isinstance(val, val_type):
        raise AssertionError(msg or f"Assert failed! Invalid type, expected {val_type} got {type(val)}")


def assertTrue(expr, msg: str = None) -> None:
    """Raises assert exception if expression is not True"""
    if not expr:
        raise AssertionError(msg or "Assert failed! Expression is false")


def assertFalse(expr, msg: str = None) -> None:
    """Raises exception if expression is not False"""
    if expr:
        raise AssertionError(msg or "Assert failed! Expression is true")
