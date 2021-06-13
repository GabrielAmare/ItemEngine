from item_engine import CASE
from item_engine.elements import IE_SyntaxError
from item_engine.textbase.items.chars import Char
from item_engine.textbase.items.tokens import Token
from typing import Iterator


__all__ = ['tokenizer']


def tokenizer_propagator(cur: Token, old: Char) -> CASE:
    if cur.value == 0:
        if old.value in '\t\n ':
            return '∈', 15
        elif old.value == '!':
            return '∈', 'EXC'
        elif old.value == '"':
            return '∈', 12
        elif old.value == "'":
            return '∈', 13
        elif old.value == '(':
            return '∈', 'LP'
        elif old.value == ')':
            return '∈', 'RP'
        elif old.value == '*':
            return '∈', 'STAR'
        elif old.value == '.':
            return '∈', 'DOT'
        elif old.value == '=':
            return '∈', 'EQUAL'
        elif old.value == '@':
            return '∈', 16
        elif old.value in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_abdefhijklmnpqrstuvwxyz':
            return '∈', 14
        elif old.value == '[':
            return '∈', 'LB'
        elif old.value == ']':
            return '∈', 'RB'
        elif old.value == 'c':
            return '∈', 17
        elif old.value == 'g':
            return '∈', 18
        elif old.value == 'o':
            return '∈', 19
        elif old.value == '{':
            return '∈', 'LS'
        elif old.value == '|':
            return '∈', 'VBAR'
        elif old.value == '}':
            return '∈', 'RS'
        else:
            return '∉', '!ATversionCOLON'
    elif cur.value == 1:
        if old.value == 'a':
            return '∈', 3
        else:
            return '∉', '!ATlangCOLON'
    elif cur.value == 2:
        if old.value == 'g':
            return '∈', 4
        else:
            return '∉', '!ATlangCOLON'
    elif cur.value == 3:
        if old.value == 'n':
            return '∈', 2
        else:
            return '∉', '!ATlangCOLON'
    elif cur.value == 4:
        if old.value == ':':
            return '∈', 'ATlangCOLON'
        else:
            return '∉', '!ATlangCOLON'
    elif cur.value == 5:
        if old.value == 'e':
            return '∈', 9
        else:
            return '∉', '!ATversionCOLON'
    elif cur.value == 6:
        if old.value == 'i':
            return '∈', 8
        else:
            return '∉', '!ATversionCOLON'
    elif cur.value == 7:
        if old.value == 'n':
            return '∈', 11
        else:
            return '∉', '!ATversionCOLON'
    elif cur.value == 8:
        if old.value == 'o':
            return '∈', 7
        else:
            return '∉', '!ATversionCOLON'
    elif cur.value == 9:
        if old.value == 'r':
            return '∈', 10
        else:
            return '∉', '!ATversionCOLON'
    elif cur.value == 10:
        if old.value == 's':
            return '∈', 6
        else:
            return '∉', '!ATversionCOLON'
    elif cur.value == 11:
        if old.value == ':':
            return '∈', 'ATversionCOLON'
        else:
            return '∉', '!ATversionCOLON'
    elif cur.value == 12:
        if old.value == '"':
            return '∈', 'STR'
        elif old.value == 'EOF':
            return '∉', '!STR'
        else:
            return '∈', 12
    elif cur.value == 13:
        if old.value == "'":
            return '∈', 'STR'
        elif old.value == 'EOF':
            return '∉', '!STR'
        else:
            return '∈', 13
    elif cur.value == 14:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 14
        else:
            return '∉', 'VAR'
    elif cur.value == 15:
        if old.value in '\t\n ':
            return '∈', 15
        else:
            return '∉', 'WHITESPACE'
    elif cur.value == 16:
        if old.value == 'l':
            return '∈', 1
        elif old.value == 'v':
            return '∈', 5
        else:
            return '∉', '!ATversionCOLON'
    elif cur.value == 17:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 14
        elif old.value == ':':
            return '∈', 'cCOLON'
        else:
            return '∉', 'VAR'
    elif cur.value == 18:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 14
        elif old.value == ':':
            return '∈', 'gCOLON'
        else:
            return '∉', 'VAR'
    elif cur.value == 19:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 14
        elif old.value == ':':
            return '∈', 'oCOLON'
        else:
            return '∉', 'VAR'
    else:
        raise Exception(f'value = {cur.value!r}')


def tokenizer_generator(src: Iterator[Char]) -> Iterator[Token]:
    cur: Token = Token.cursor(0)
    for old in src:
        while cur.to == old.at:
            new: Token = cur.develop(tokenizer_propagator(cur, old), old)
            if not isinstance(new.value, str):
                if new.to == old.to:
                    cur: Token = new
                else:
                    raise IE_SyntaxError(new)
            elif not new.value.startswith('!'):
                yield new
                cur: Token = Token.cursor(new.to)
                continue
            else:
                if old.value == 'EOF':
                    break
                else:
                    raise IE_SyntaxError(new)
    yield cur.eof()


def tokenizer_skips(src: Iterator[Token]) -> Iterator[Token]:
    for inp in src:
        if inp.value == 'WHITESPACE':
            continue
        yield inp


def tokenizer_reassign(src: Iterator[Token]) -> Iterator[Token]:
    for pos, inp in enumerate(src):
        if inp.to > inp.at:
            yield inp.replace(at=pos, to=pos + 1)
        else:
            yield inp.replace(at=pos, to=pos)


def tokenizer(src: Iterator[Char]) -> Iterator[Token]:
    return tokenizer_reassign(tokenizer_skips(tokenizer_generator(src)))
