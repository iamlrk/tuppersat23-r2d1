"""


"""

def Counter(start=0x00, modulo=None):
    """Callable that counts from start every time it is called."""
    _count = start

    def _counter():
        nonlocal _count
        idx = _count
        # update counter
        _count += 1
        if modulo:
            _count %= modulo
        return idx

    return _counter
