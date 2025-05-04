from weakref import WeakKeyDictionary

lookup = WeakKeyDictionary()

def register(obj, paracls):
    'Instantiate paracls, set `obj` to be the regular object associated with the new parabject, and return the parabject.'
    parabject = paracls()
    lookup[parabject] = obj
    return parabject

class UnknownParabjectException(Exception): pass

def dereference(parabject):
    'Get the regular object associated with `parabject` or raise UnknownParabjectException.'
    try:
        return lookup[parabject]
    except (KeyError, TypeError):
        raise UnknownParabjectException

class Parabject:
    'Subclasses typically implement `__getattr__` for dynamic behaviour on attribute access.'

    def __neg__(self):
        'Dereference this parabject.'
        return dereference(self)
