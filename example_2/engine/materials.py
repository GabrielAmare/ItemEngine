from item_engine.textbase import *
from itertools import starmap
from operator import eq


class Match:
    def __init__(self, c0):
        self.c0 = c0
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r})'
    
    def __str__(self):
        return f'{{{self.c0!s}}}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0


class MatchAs:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{{{self.c0!s}!{self.c1!s}}}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class MatchIn:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{{{self.c0!s}*{self.c1!s}}}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Literal:
    def __init__(self, c0):
        self.c0 = c0
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r})'
    
    def __str__(self):
        return f'{self.c0!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0


class And:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s}{self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Or:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s}|{self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Repeat:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s}.{self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Operator:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s}={self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Grammar:
    def __init__(self, *cs):
        self.cs = cs
    
    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(map(repr, self.cs))})"
    
    def __str__(self):
        return '\n'.join(map(str, self.cs))
    
    def __eq__(self, other):
        return type(self) is type(other) and all(starmap(eq, zip(self.cs, other.cs)))


def build(e: Element):
    if isinstance(e, Lemma):
        if e.value == '__MATCH__':
            return Match(build(e.data['c0']))
        elif e.value == '__MATCHAS__':
            return MatchAs(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__MATCHIN__':
            return MatchIn(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__LITERAL__':
            return Literal(build(e.data['c0']))
        elif e.value == '__AND__':
            return And(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__OR__':
            return Or(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__REPEAT__':
            return Repeat(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__OPERATOR__':
            return Operator(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__GRAMMAR__':
            return Grammar(*map(build, e.data['cs']))
        else:
            raise Exception(e.value)
    elif isinstance(e, Token):
        return e.content
    else:
        raise Exception(e.value)
