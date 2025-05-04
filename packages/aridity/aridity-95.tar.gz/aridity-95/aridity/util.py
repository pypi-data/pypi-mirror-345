from contextlib import contextmanager
from importlib.metadata import entry_points
import sys

dotpy = '.py'
inf = float('inf')
null_exc_info = None, None, None

class NoSuchPathException(Exception): pass

class UnparseNoSuchPathException(NoSuchPathException):

    def __str__(self):
        path, = self.args
        return ' '.join(path)

class TreeNoSuchPathException(NoSuchPathException):

    def __str__(self):
        path, causes = self.args # XXX: Also collect (and show) where in the tree the causes happened?
        causestrtocount = {}
        for causestr in map(str, causes):
            try:
                causestrtocount[causestr] += 1
            except KeyError:
                causestrtocount[causestr] = 1
        lines = [' '.join(path)]
        for causestr, count in causestrtocount.items():
            causelines = causestr.splitlines()
            lines.append(f"{count}x {causelines[0]}")
            for l in causelines[1:]:
                lines.append(f"    {l}")
        return '\n'.join(lines)

class CycleException(UnparseNoSuchPathException): pass

class UnsupportedEntryException(Exception): pass

def openresource(package_or_name, resource_name, encoding = 'ascii'):
    'Like `pkg_resources.resource_stream` but text mode.'
    from .model import Resource
    return Resource(package_or_name, resource_name, encoding).open(False)

def solo(v):
    'Assert exactly one object in the given sequence and return it.'
    x, = v
    return x

def qualname(obj):
    try:
        return obj.__qualname__
    except AttributeError:
        name = obj.__name__
        if getattr(sys.modules[obj.__module__], name) is not obj:
            raise
        return name

def selectentrypoints(group):
    obj = entry_points()
    try:
        select = obj.select
    except AttributeError:
        return obj[group]
    return select(group = group)

def popattr(obj, name):
    val = getattr(obj, name)
    delattr(obj, name)
    return val

class Forkable:

    @classmethod
    def _of(cls, *args, **kwargs):
        return cls(*args, **kwargs)

class Burial:

    name = 'burial'

    @classmethod
    def value(cls, e):
        return getattr(e, cls.name, 0)

    @classmethod
    @contextmanager
    def bumping(cls, exctype):
        try:
            yield
        except exctype as e:
            setattr(e, cls.name, cls.value(e) + 1)
            raise
