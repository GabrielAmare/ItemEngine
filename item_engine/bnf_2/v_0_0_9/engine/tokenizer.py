from item_engine import CASE
from item_engine.elements import IE_SyntaxError
from item_engine.textbase.items.chars import Char
from item_engine.textbase.items.tokens import Token
from typing import Iterator


__all__ = ['tokenizer']


def tokenizer_propagator(cur: Token, old: Char) -> CASE:
    if cur.value == 0:
        if old.value in '\t\n ':
            return '∈', 24
        elif old.value == '"':
            return '∈', 22
        elif old.value == "'":
            return '∈', 26
        elif old.value == '(':
            return '∈', 'LP'
        elif old.value == ')':
            return '∈', 'RP'
        elif old.value == '+':
            return '∈', 'PLUS'
        elif old.value == '.':
            return '∈', 'DOT'
        elif old.value == '=':
            return '∈', 'EQUAL'
        elif old.value == '@':
            return '∈', 25
        elif old.value in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_bdefhjklmqstuvwxyz':
            return '∈', 27
        elif old.value == '[':
            return '∈', 'LB'
        elif old.value == ']':
            return '∈', 'RB'
        elif old.value == '^':
            return '∈', 'HAT'
        elif old.value == 'a':
            return '∈', 29
        elif old.value == 'c':
            return '∈', 30
        elif old.value == 'g':
            return '∈', 31
        elif old.value == 'i':
            return '∈', 33
        elif old.value == 'n':
            return '∈', 34
        elif old.value == 'o':
            return '∈', 37
        elif old.value == 'p':
            return '∈', 45
        elif old.value == 'r':
            return '∈', 48
        elif old.value == '{':
            return '∈', 'LS'
        elif old.value == '|':
            return '∈', 'VBAR'
        elif old.value == '}':
            return '∈', 'RS'
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
        else:
            return '∈', 23
    elif cur.value == 24:
        if old.value in '\t\n ':
            return '∈', 24
        else:
            return '∉', 'WHITESPACE'
    elif cur.value == 25:
        if old.value == 'l':
            return '∈', 1
        elif old.value == 'v':
            return '∈', 5
        elif old.value == 'w':
            return '∈', 16
        else:
            return '∉', '!ATwhitespaceCOLON'
    elif cur.value == 26:
        if old.value == "'":
            return '∈', 'STR'
        elif old.value == 'EOF':
            return '∈', 23
        else:
            return '∈', 26
    elif cur.value == 27:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 27
        else:
            return '∉', 'VAR'
    elif cur.value == 28:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 27
        else:
            return '∉', 'as'
    elif cur.value == 29:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrtuvwxyz':
            return '∈', 27
        elif old.value == 's':
            return '∈', 28
        else:
            return '∉', 'VAR'
    elif cur.value == 30:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 27
        elif old.value == ':':
            return '∈', 'cCOLON'
        else:
            return '∉', 'VAR'
    elif cur.value == 31:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 27
        elif old.value == ':':
            return '∈', 'gCOLON'
        else:
            return '∉', 'VAR'
    elif cur.value == 32:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 27
        else:
            return '∉', 'in'
    elif cur.value == 33:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmopqrstuvwxyz':
            return '∈', 27
        elif old.value == 'n':
            return '∈', 32
        else:
            return '∉', 'VAR'
    elif cur.value == 34:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnpqrstuvwxyz':
            return '∈', 27
        elif old.value == 'o':
            return '∈', 36
        else:
            return '∉', 'VAR'
    elif cur.value == 35:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 27
        else:
            return '∉', 'not'
    elif cur.value == 36:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrsuvwxyz':
            return '∈', 27
        elif old.value == 't':
            return '∈', 35
        else:
            return '∉', 'VAR'
    elif cur.value == 37:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnoqrstuvwxyz':
            return '∈', 27
        elif old.value == ':':
            return '∈', 'oCOLON'
        elif old.value == 'p':
            return '∈', 42
        else:
            return '∉', 'VAR'
    elif cur.value == 38:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_bcdefghijklmnopqrstuvwxyz':
            return '∈', 27
        elif old.value == 'a':
            return '∈', 44
        else:
            return '∉', 'VAR'
    elif cur.value == 39:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghjklmnopqrstuvwxyz':
            return '∈', 27
        elif old.value == 'i':
            return '∈', 41
        else:
            return '∉', 'VAR'
    elif cur.value == 40:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmopqrstuvwxyz':
            return '∈', 27
        elif old.value == 'n':
            return '∈', 38
        else:
            return '∉', 'VAR'
    elif cur.value == 41:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnpqrstuvwxyz':
            return '∈', 27
        elif old.value == 'o':
            return '∈', 40
        else:
            return '∉', 'VAR'
    elif cur.value == 42:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrsuvwxyz':
            return '∈', 27
        elif old.value == 't':
            return '∈', 39
        else:
            return '∉', 'VAR'
    elif cur.value == 43:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 27
        else:
            return '∉', 'optional'
    elif cur.value == 44:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijkmnopqrstuvwxyz':
            return '∈', 27
        elif old.value == 'l':
            return '∈', 43
        else:
            return '∉', 'VAR'
    elif cur.value == 45:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 27
        elif old.value == ':':
            return '∈', 'pCOLON'
        else:
            return '∉', 'VAR'
    elif cur.value == 46:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_bcdefghijklmnopqrstuvwxyz':
            return '∈', 27
        elif old.value == 'a':
            return '∈', 51
        else:
            return '∉', 'VAR'
    elif cur.value == 47:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdfghijklmnopqrstuvwxyz':
            return '∈', 27
        elif old.value == 'e':
            return '∈', 46
        else:
            return '∉', 'VAR'
    elif cur.value == 48:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdfghijklmnopqrstuvwxyz':
            return '∈', 27
        elif old.value == 'e':
            return '∈', 49
        else:
            return '∉', 'VAR'
    elif cur.value == 49:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnoqrstuvwxyz':
            return '∈', 27
        elif old.value == 'p':
            return '∈', 47
        else:
            return '∉', 'VAR'
    elif cur.value == 50:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 27
        else:
            return '∉', 'repeat'
    elif cur.value == 51:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrsuvwxyz':
            return '∈', 27
        elif old.value == 't':
            return '∈', 50
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
                    print(repr(cur), repr(old), repr(new))
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
