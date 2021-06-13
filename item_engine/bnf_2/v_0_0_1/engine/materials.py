from __future__ import annotations
from item_engine.textbase.items.lemmas import Lemma
from item_engine.textbase.items.tokens import Token
from typing import List


# this module has been auto-generated by ItemEngine


__all__ = ['Any_', 'All_', 'CharsetArg', 'PatternArg', 'GrammarArg', 'Atom_', 'Str', 'Var', 'Match', 'MatchAs', 'MatchIn', 'All', 'Any', 'Optional', 'Repeat', 'Enum', 'Charset', 'Pattern', 'Operator', 'Group', 'Grammar', 'build']


class Any_:
    pass


class All_(Any_):
    pass


class CharsetArg:
    pass


class PatternArg:
    pass


class GrammarArg:
    pass


class Atom_(All_):
    pass


class Str(Atom_, CharsetArg, PatternArg):
    def __init__(self, expr: str):
        self.expr: str = expr
    
    def __str__(self):
        return str(self.expr)
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.expr!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.expr == other.expr
        else:
            return NotImplemented
    
    __hash__ = None


class Var(CharsetArg, PatternArg):
    def __init__(self, name: str):
        self.name: str = name
    
    def __str__(self):
        return str(self.name)
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.name == other.name
        else:
            return NotImplemented
    
    __hash__ = None


class Match(Atom_):
    def __init__(self, name: str):
        self.name: str = name
    
    def __str__(self):
        return '{' + str(self.name) + '}'
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.name == other.name
        else:
            return NotImplemented
    
    __hash__ = None


class MatchAs(Atom_):
    def __init__(self, name: str, key: str):
        self.name: str = name
        self.key: str = key
    
    def __str__(self):
        return '{' + str(self.name) + ' !' + str(self.key) + '}'
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r}, {self.key!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.name == other.name and self.key == other.key
        else:
            return NotImplemented
    
    __hash__ = None


class MatchIn(Atom_):
    def __init__(self, name: str, key: str):
        self.name: str = name
        self.key: str = key
    
    def __str__(self):
        return '{' + str(self.name) + ' *' + str(self.key) + '}'
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r}, {self.key!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.name == other.name and self.key == other.key
        else:
            return NotImplemented
    
    __hash__ = None


class All(All_):
    def __init__(self, args: List[Atom_]):
        self.args: List[Atom_] = args
    
    def __str__(self):
        return ' '.join(map(str, self.args))
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.args!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.args == other.args
        else:
            return NotImplemented
    
    __hash__ = None


class Any(Any_):
    def __init__(self, args: List[All_]):
        self.args: List[All_] = args
    
    def __str__(self):
        return ' | '.join(map(str, self.args))
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.args!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.args == other.args
        else:
            return NotImplemented
    
    __hash__ = None


class Optional(Atom_):
    def __init__(self, child: Any_):
        self.child: Any_ = child
    
    def __str__(self):
        return '[' + str(self.child) + ']'
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.child!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.child == other.child
        else:
            return NotImplemented
    
    __hash__ = None


class Repeat(Atom_):
    def __init__(self, child: Any_):
        self.child: Any_ = child
    
    def __str__(self):
        return '(' + str(self.child) + ')'
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.child!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.child == other.child
        else:
            return NotImplemented
    
    __hash__ = None


class Enum(Atom_):
    def __init__(self, separator: Str, child: MatchIn):
        self.separator: Str = separator
        self.child: MatchIn = child
    
    def __str__(self):
        return str(self.separator) + '.' + str(self.child)
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.separator!r}, {self.child!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.separator == other.separator and self.child == other.child
        else:
            return NotImplemented
    
    __hash__ = None


class Charset(GrammarArg):
    def __init__(self, name: str, args: List[CharsetArg]):
        self.name: str = name
        self.args: List[CharsetArg] = args
    
    def __str__(self):
        return 'c:' + str(self.name) + ' = ' + ' '.join(map(str, self.args))
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r}, {self.args!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.name == other.name and self.args == other.args
        else:
            return NotImplemented
    
    __hash__ = None


class Pattern:
    def __init__(self, name: str, args: List[PatternArg]):
        self.name: str = name
        self.args: List[PatternArg] = args
    
    def __str__(self):
        return 'p:' + str(self.name) + ' = ' + ' '.join(map(str, self.args))
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r}, {self.args!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.name == other.name and self.args == other.args
        else:
            return NotImplemented
    
    __hash__ = None


class Operator(GrammarArg):
    def __init__(self, name: str, rule: Any_):
        self.name: str = name
        self.rule: Any_ = rule
    
    def __str__(self):
        return 'o:' + str(self.name) + ' = ' + str(self.rule)
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r}, {self.rule!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.name == other.name and self.rule == other.rule
        else:
            return NotImplemented
    
    __hash__ = None


class Group(GrammarArg):
    def __init__(self, name: str, names: List[str]):
        self.name: str = name
        self.names: List[str] = names
    
    def __str__(self):
        return 'g:' + str(self.name) + ' = ' + ' | '.join(map(str, self.names))
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r}, {self.names!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.name == other.name and self.names == other.names
        else:
            return NotImplemented
    
    __hash__ = None


class Grammar:
    def __init__(self, lang: str, version: str, whitespace: str, args: List[GrammarArg]):
        self.lang: str = lang
        self.version: str = version
        self.whitespace: str = whitespace
        self.args: List[GrammarArg] = args
    
    def __str__(self):
        return '@lang:' + str(self.lang) + '\n' + '@version:' + str(self.version) + '\n' + '@whitespace:' + str(self.whitespace) + '\n' + '\n'.join(map(str, self.args))
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.lang!r}, {self.version!r}, {self.whitespace!r}, {self.args!r})'
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.lang == other.lang and self.version == other.version and self.whitespace == other.whitespace and self.args == other.args
        else:
            return NotImplemented
    
    __hash__ = None


def build(obj):
    if isinstance(obj, Lemma):
        if obj.value == 'Str':
            return Str(expr=build(obj.data['expr']))
        elif obj.value == 'Var':
            return Var(name=build(obj.data['name']))
        elif obj.value == 'Match':
            return Match(name=build(obj.data['name']))
        elif obj.value == 'MatchAs':
            return MatchAs(name=build(obj.data['name']), key=build(obj.data['key']))
        elif obj.value == 'MatchIn':
            return MatchIn(name=build(obj.data['name']), key=build(obj.data['key']))
        elif obj.value == 'All':
            return All(args=list(map(build, obj.data['args'])))
        elif obj.value == 'Any':
            return Any(args=list(map(build, obj.data['args'])))
        elif obj.value == 'Optional':
            return Optional(child=build(obj.data['child']))
        elif obj.value == 'Repeat':
            return Repeat(child=build(obj.data['child']))
        elif obj.value == 'Enum':
            return Enum(separator=build(obj.data['separator']), child=build(obj.data['child']))
        elif obj.value == 'Charset':
            return Charset(name=build(obj.data['name']), args=list(map(build, obj.data['args'])))
        elif obj.value == 'Pattern':
            return Pattern(name=build(obj.data['name']), args=list(map(build, obj.data['args'])))
        elif obj.value == 'Operator':
            return Operator(name=build(obj.data['name']), rule=build(obj.data['rule']))
        elif obj.value == 'Group':
            return Group(name=build(obj.data['name']), names=list(map(build, obj.data['names'])))
        elif obj.value == 'Grammar':
            return Grammar(lang=build(obj.data['lang']), version=build(obj.data['version']), whitespace=build(obj.data['whitespace']), args=list(map(build, obj.data['args'])))
        else:
            raise ValueError(obj.value)
    elif isinstance(obj, Token):
        return obj.content
    else:
        raise TypeError(type(obj))
