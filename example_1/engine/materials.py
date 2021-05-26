from item_engine.textbase import *


class Var:
    def __init__(self, name: str):
        self.name: str = name
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r})'
    
    def __str__(self):
        return str(self.name)
    
    def __eq__(self, other):
        return type(self) is type(other) and self.name == other.name


class Int:
    def __init__(self, value: int):
        self.value: int = value
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.value!r})'
    
    def __str__(self):
        return str(self.value)
    
    def __eq__(self, other):
        return type(self) is type(other) and self.value == other.value


class Add:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s} + {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


def build(e: Element):
    if isinstance(e, Lemma):
        if e.value == '__ADD__':
            return Add(build(e.data['c0']), build(e.data['c1']))
        else:
            raise Exception(e.value)
    elif isinstance(e, Token):
        if e.value == 'VAR':
            return Var(str(e.content))
        elif e.value == 'INT':
            return Int(int(e.content))
        else:
            return e.content
    else:
        raise Exception(e.value)
