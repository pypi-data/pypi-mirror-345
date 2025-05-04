from .model import Blank, Boolean, Boundary, Call, Concat, Entry, nullmonitor, Number, Text
from decimal import Decimal
from functools import partial, reduce
from pyparsing import Forward, Literal, MatchFirst, NoMatch, OneOrMore, Optional, Regex, Suppress, ZeroOrMore
import operator, re

class AnyScalar:

    numbermatch = re.compile('-?(?:[0-9]+(?:[.][0-9]*)?|[.][0-9]+)').fullmatch
    booleans = {t: Boolean(b).augment(textvalue = t) for b in map(bool, range(2)) for t in [str(b).lower()]}

    @classmethod
    def pa(cls, s, l, t):
        text, = t
        try:
            return cls.booleans[text]
        except KeyError:
            m = cls.numbermatch(text)
        if m is None:
            return Text(text)
        if '.' in text:
            val = Decimal(text)
        else:
            val = int(text)
            if not val and '-' == text[0]:
                val = Decimal(text) # Preserve sign.
        return Number(val).augment(textvalue = text)

def _gettext(notchars, pa):
    return Regex(fr"[^$\s{re.escape(notchars)}]+").leaveWhitespace().setParseAction(pa)

def _getarg(callchain, scalarpa, boundarychars):
    gettext = partial(_gettext, boundarychars)
    opttext = Optional(gettext(Text.pa))
    return (OneOrMore(opttext + callchain) + opttext | gettext(scalarpa)).setParseAction(Concat.smartpa)

def _bracketed(callchain, blankpa, scalarpa, o, c):
    gettext = partial(_gettext, o + c)
    bracketed = Forward()
    chainorbrackets = callchain | (Literal(o).setParseAction(Text.pa) + bracketed + Literal(c).setParseAction(Text.pa)).leaveWhitespace()
    opttext = Optional(gettext(Text.pa))
    concat = OneOrMore(opttext + chainorbrackets) + opttext
    optblank = _getoptblank(blankpa, '')
    bracketed << ZeroOrMore(optblank + (concat | gettext(scalarpa)).setParseAction(Concat.smartpa)) + optblank
    return bracketed

def _literalbracketed(o, c):
    bracketed = Forward()
    brackets = (Literal(o) + bracketed + Literal(c)).leaveWhitespace()
    opttext = Regex(f"[^{re.escape(o + c)}]*").leaveWhitespace()
    bracketed << ZeroOrMore(opttext + brackets) + opttext
    return bracketed

def _getoptblank(pa, boundarychars):
    return Optional(Regex(fr"[^\S{re.escape(boundarychars)}]+").leaveWhitespace().setParseAction(pa))

class Parser:

    def __init__(self, g, singleton = True):
        self.g = g.parseWithTabs()
        self.singleton = singleton

    def __call__(self, text):
        result = self.g.parseString(text, parseAll = True).asList()
        if self.singleton:
            result, = result
        return result

def _principalcallpa(s, l, t):
    return Call(t[0], t[2:-1], t[1] + t[-1])

def _additionalcallpa(s, l, t):
    return Call(t[0], t[1:], ['', ''])

class GFactory:

    bracketpairs = '()', '[]'
    identifier = Regex(fr"[^\s${''.join(re.escape(o) for o, _ in bracketpairs)}]*")

    def __init__(self, scalarpa = AnyScalar.pa, boundarychars = '\r\n', ormorecls = OneOrMore, monitor = nullmonitor):
        self.scalarpa = scalarpa
        self.boundarychars = boundarychars
        self.ormorecls = ormorecls
        self.monitor = monitor

    def templatepa(self, s, l, t):
        return Concat(t, self.monitor)

    def _bracketspa(self, s, l, t):
        return Concat(t[1:-1] or [Text('')], self.monitor)

    def create(self, pa):
        def itercalls():
            def getbrackets(blankpa, scalarpa):
                return Literal(o) + _bracketed(callchain, blankpa, scalarpa, o, c) + Literal(c)
            for o, c in self.bracketpairs:
                yield (Suppress(Regex("[$](?:lit|')")) + Suppress(o) + _literalbracketed(o, c) + Suppress(c)).setParseAction(Text.joinpa)
                yield (Suppress(Regex('[$](?:pass|[.])')) + getbrackets(Text.pa, Text.pa)).setParseAction(self._bracketspa)
                yield (Suppress('$') + self.identifier + getbrackets(Blank.pa, AnyScalar.pa)).setParseAction(_principalcallpa)
                yield (Suppress('$') + self.identifier + callchain).setParseAction(_additionalcallpa)
        optblank = _getoptblank(Blank.pa, self.boundarychars)
        callchain = Forward()
        callchain << MatchFirst(itercalls()).leaveWhitespace()
        return reduce(operator.add, [
            self.ormorecls(optblank + _getarg(callchain, self.scalarpa, self.boundarychars)),
            optblank,
            Optional(Regex(f"[{re.escape(self.boundarychars)}]+").leaveWhitespace().setParseAction(Boundary.pa) if self.boundarychars else NoMatch()),
        ]).setParseAction(pa)

commandparser = Parser(GFactory(ormorecls = ZeroOrMore).create(Entry.pa))

def templateparser(monitor):
    gfactory = GFactory(scalarpa = Text.pa, boundarychars = '', monitor = monitor)
    return Parser(gfactory.create(gfactory.templatepa) | Regex('^$').setParseAction(Text.pa))
