from .grammar import commandparser
from .model import Entry
from pyparsing import ParseException

class DanglingStackException(Exception): pass

class NoSuchIndentException(Exception): pass

class MalformedEntryException(Exception): pass

class Suffix:

    def __init__(self, entry):
        self.indent = entry.indent()
        self.entry = entry

    def closing(self, contextindent):
        if any(x != y for x, y in zip(self.indent, contextindent)):
            raise MalformedEntryException(self.entry)
        return len(self.indent) <= len(contextindent)

class Command:

    def __init__(self, entry):
        self.size = entry.size()
        self.entry = entry

emptyentry = Entry([])
emptysuffix = Suffix(emptyentry)

class CommandReader:

    def __init__(self, stream, rootprefix = emptyentry):
        self.stack = []
        self.partials = {'': emptyentry}
        self.stream = stream
        self.rootprefix = rootprefix
        for _ in self._update(False, emptysuffix):
            assert False

    def _readcommands(self, line):
        try:
            suffix = Suffix(commandparser(''.join([*self.stack, line])))
            del self.stack[:]
        except ParseException:
            self.stack.append(line)
            return
        fire = suffix.closing(self.indent)
        if not fire:
            self.partials[suffix.indent] = self.command.entry
        elif suffix.indent not in self.partials:
            raise NoSuchIndentException(suffix.entry)
        for i in list(self.partials):
            if len(suffix.indent) < len(i):
                del self.partials[i]
        yield from self._update(fire, suffix)

    def _update(self, fire, suffix):
        command = self.rootprefix.plus(self.command.entry) if fire and self.command.size else None
        self.command = Command(self.partials[suffix.indent].plus(suffix.entry))
        self.indent = suffix.indent
        if command is not None:
            yield command

    def __iter__(self):
        for line in self.stream:
            yield from self._readcommands(line)
        if self.stack:
            raise DanglingStackException(self.stack)
        yield from self._update(True, emptysuffix)

    def pipeto(self, scope):
        for command in self:
            scope.execute(command)
