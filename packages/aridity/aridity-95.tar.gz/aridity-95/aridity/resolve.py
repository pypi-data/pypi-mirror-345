from .search import Query
from .util import CycleException, Forkable, NoSuchPathException, TreeNoSuchPathException

class BaseResolveContext:

    @property
    def label(self):
        return self.leafscope().label

    @property
    def parents(self):
        return self.leafscope().parents

    @property
    def resolvables(self):
        return self.leafscope().resolvables

    def createchild(self):
        return self.leafscope().createchild()

    def getresolvecontext(self):
        return self

    def resolvableornone(self, key):
        return self.leafscope().resolvableornone(key)

    def resolved(self, *path):
        return self.resolvedimpl(path) if path else self.leafscope()

    def staticscope(self):
        return self.leafscope().staticscope()

class AnchorResolveContext(BaseResolveContext):

    def __init__(self, anchorscope):
        self.anchorscope = anchorscope

    def leafscope(self):
        return self.anchorscope

    def resolvedimpl(self, path):
        hit = Query([], path).search(self.anchorscope)
        return hit.resolvable.resolve(ResolveContext(self.anchorscope, path, [hit.address]))

class ResolveContext(BaseResolveContext, Forkable):

    def __init__(self, anchorscope, exprpath, addresses):
        self.anchorscope = anchorscope
        self.scopepath = exprpath[:-1]
        self.exprpath = exprpath
        self.addresses = addresses

    def leafscope(self):
        return Query([], self.scopepath).search(self.anchorscope).naiveresolve() if self.scopepath else self.anchorscope # XXX: Is naiveresolve correct here?

    def resolvedimpl(self, path):
        try:
            hit = Query(self.scopepath, path).search(self.anchorscope)
            if hit.address in self.addresses: # XXX: Could it be valid to resolve the same address recursively with 2 different contexts?
                raise CycleException(path)
            return hit.resolvable.resolve(self._of(self.anchorscope, [*self.scopepath, *path], [*self.addresses, hit.address]))
        except NoSuchPathException as e:
            raise TreeNoSuchPathException(self.exprpath, [e])
