from item_engine import CASE
from item_engine.elements import IE_SyntaxError
from item_engine.textbase.items.chars import Char
from item_engine.textbase.items.tokens import Token
from typing import Iterator


__all__ = ['tokenizer']


def tokenizer_propagator(cur: Token, old: Char) -> CASE:
    if cur.value == 0:
        if old.value in '\t\n ':
            return '∈', 25
        elif old.value == '!':
            return '∈', 'EXC'
        elif old.value == '"':
            return '∈', 22
        elif old.value == "'":
            return '∈', 23
        elif old.value == '(':
            return '∈', 'LP'
        elif old.value == ')':
            return '∈', 'RP'
        elif old.value == '*':
            return '∈', 'STAR'
        elif old.value == '+':
            return '∈', 'PLUS'
        elif old.value == '.':
            return '∈', 'DOT'
        elif old.value == '=':
            return '∈', 'EQUAL'
        elif old.value == '?':
            return '∈', 'INTER'
        elif old.value == '@':
            return '∈', 26
        elif old.value in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_abdefhijklmnqrstuvwxyz':
            return '∈', 24
        elif old.value == '[':
            return '∈', 'LB'
        elif old.value == ']':
            return '∈', 'RB'
        elif old.value == '^':
            return '∈', 'HAT'
        elif old.value == 'c':
            return '∈', 27
        elif old.value == 'g':
            return '∈', 28
        elif old.value == 'o':
            return '∈', 29
        elif old.value == 'p':
            return '∈', 30
        elif old.value == '{':
            return '∈', 'LS'
        elif old.value == '|':
            return '∈', 'VBAR'
        elif old.value == '}':
            return '∈', 'RS'
        elif old.value == '~':
            return '∈', 'WAVE'
        else:
            return '∉', '!ATwhitespaceCOLON'
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
        if old.value == 'a':
            return '∈', 13
        else:
            return '∉', '!ATwhitespaceCOLON'
    elif cur.value == 13:
        if old.value == 'c':
            return '∈', 14
        else:
            return '∉', '!ATwhitespaceCOLON'
    elif cur.value == 14:
        if old.value == 'e':
            return '∈', 21
        else:
            return '∉', '!ATwhitespaceCOLON'
    elif cur.value == 15:
        if old.value == 'e':
            return '∈', 19
        else:
            return '∉', '!ATwhitespaceCOLON'
    elif cur.value == 16:
        if old.value == 'h':
            return '∈', 17
        else:
            return '∉', '!ATwhitespaceCOLON'
    elif cur.value == 17:
        if old.value == 'i':
            return '∈', 20
        else:
            return '∉', '!ATwhitespaceCOLON'
    elif cur.value == 18:
        if old.value == 'p':
            return '∈', 12
        else:
            return '∉', '!ATwhitespaceCOLON'
    elif cur.value == 19:
        if old.value == 's':
            return '∈', 18
        else:
            return '∉', '!ATwhitespaceCOLON'
    elif cur.value == 20:
        if old.value == 't':
            return '∈', 15
        else:
            return '∉', '!ATwhitespaceCOLON'
    elif cur.value == 21:
        if old.value == ':':
            return '∈', 'ATwhitespaceCOLON'
        else:
            return '∉', '!ATwhitespaceCOLON'
    elif cur.value == 22:
        if old.value == '"':
            return '∈', 'STR'
        elif old.value == 'EOF':
            return '∉', '!STR'
        else:
            return '∈', 22
    elif cur.value == 23:
        if old.value == "'":
            return '∈', 'STR'
        elif old.value == 'EOF':
            return '∉', '!STR'
        else:
            return '∈', 23
    elif cur.value == 24:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 24
        else:
            return '∉', 'VAR'
    elif cur.value == 25:
        if old.value in '\t\n ':
            return '∈', 25
        else:
            return '∉', 'WHITESPACE'
    elif cur.value == 26:
        if old.value == 'l':
            return '∈', 1
        elif old.value == 'v':
            return '∈', 5
        elif old.value == 'w':
            return '∈', 16
        else:
            return '∉', '!ATwhitespaceCOLON'
    elif cur.value == 27:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 24
        elif old.value == ':':
            return '∈', 'cCOLON'
        else:
            return '∉', 'VAR'
    elif cur.value == 28:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 24
        elif old.value == ':':
            return '∈', 'gCOLON'
        else:
            return '∉', 'VAR'
    elif cur.value == 29:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 24
        elif old.value == ':':
            return '∈', 'oCOLON'
        else:
            return '∉', 'VAR'
    elif cur.value == 30:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 24
        elif old.value == ':':
            return '∈', 'pCOLON'
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
