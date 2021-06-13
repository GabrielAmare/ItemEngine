from item_engine import CASE
from item_engine.elements import IE_SyntaxError
from item_engine.textbase.items.chars import Char
from item_engine.textbase.items.tokens import Token
from typing import Iterator


__all__ = ['tokenizer']


def tokenizer_propagator(cur: Token, old: Char) -> CASE:
    if cur.value == 0:
        if old.value in '\t\n ':
            return '∈', 4
        elif old.value == '"':
            return '∈', 1
        elif old.value == "'":
            return '∈', 2
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
        elif old.value in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_bdefhjkmqstuxyz':
            return '∈', 3
        elif old.value == '[':
            return '∈', 'LB'
        elif old.value == ']':
            return '∈', 'RB'
        elif old.value == '^':
            return '∈', 'HAT'
        elif old.value == 'a':
            return '∈', 6
        elif old.value == 'c':
            return '∈', 7
        elif old.value == 'g':
            return '∈', 8
        elif old.value == 'i':
            return '∈', 10
        elif old.value == 'l':
            return '∈', 11
        elif old.value == 'n':
            return '∈', 15
        elif old.value == 'o':
            return '∈', 18
        elif old.value == 'p':
            return '∈', 26
        elif old.value == 'r':
            return '∈', 29
        elif old.value == 'v':
            return '∈', 33
        elif old.value == 'w':
            return '∈', 44
        elif old.value == '{':
            return '∈', 'LS'
        elif old.value == '|':
            return '∈', 'VBAR'
        elif old.value == '}':
            return '∈', 'RS'
        else:
            return '∉', '!whitespaceCOLON'
    elif cur.value == 1:
        if old.value == '"':
            return '∈', 'STR'
        elif old.value == 'EOF':
            return '∉', '!STR'
        else:
            return '∈', 1
    elif cur.value == 2:
        if old.value == "'":
            return '∈', 'STR'
        elif old.value == 'EOF':
            return '∉', '!STR'
        else:
            return '∈', 2
    elif cur.value == 3:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        else:
            return '∉', 'VAR'
    elif cur.value == 4:
        if old.value in '\t\n ':
            return '∈', 4
        else:
            return '∉', 'WHITESPACE'
    elif cur.value == 5:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        else:
            return '∉', 'as'
    elif cur.value == 6:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrtuvwxyz':
            return '∈', 3
        elif old.value == 's':
            return '∈', 5
        else:
            return '∉', 'VAR'
    elif cur.value == 7:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == ':':
            return '∈', 'cCOLON'
        else:
            return '∉', 'VAR'
    elif cur.value == 8:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == ':':
            return '∈', 'gCOLON'
        else:
            return '∉', 'VAR'
    elif cur.value == 9:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        else:
            return '∉', 'in'
    elif cur.value == 10:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'n':
            return '∈', 9
        else:
            return '∉', 'VAR'
    elif cur.value == 11:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_bcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'a':
            return '∈', 13
        else:
            return '∉', 'VAR'
    elif cur.value == 12:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefhijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'g':
            return '∈', 14
        else:
            return '∉', 'VAR'
    elif cur.value == 13:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'n':
            return '∈', 12
        else:
            return '∉', 'VAR'
    elif cur.value == 14:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == ':':
            return '∈', 'langCOLON'
        else:
            return '∉', 'VAR'
    elif cur.value == 15:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnpqrstuvwxyz':
            return '∈', 3
        elif old.value == 'o':
            return '∈', 17
        else:
            return '∉', 'VAR'
    elif cur.value == 16:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        else:
            return '∉', 'not'
    elif cur.value == 17:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrsuvwxyz':
            return '∈', 3
        elif old.value == 't':
            return '∈', 16
        else:
            return '∉', 'VAR'
    elif cur.value == 18:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnoqrstuvwxyz':
            return '∈', 3
        elif old.value == ':':
            return '∈', 'oCOLON'
        elif old.value == 'p':
            return '∈', 23
        else:
            return '∉', 'VAR'
    elif cur.value == 19:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_bcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'a':
            return '∈', 25
        else:
            return '∉', 'VAR'
    elif cur.value == 20:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghjklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'i':
            return '∈', 22
        else:
            return '∉', 'VAR'
    elif cur.value == 21:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'n':
            return '∈', 19
        else:
            return '∉', 'VAR'
    elif cur.value == 22:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnpqrstuvwxyz':
            return '∈', 3
        elif old.value == 'o':
            return '∈', 21
        else:
            return '∉', 'VAR'
    elif cur.value == 23:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrsuvwxyz':
            return '∈', 3
        elif old.value == 't':
            return '∈', 20
        else:
            return '∉', 'VAR'
    elif cur.value == 24:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        else:
            return '∉', 'optional'
    elif cur.value == 25:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijkmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'l':
            return '∈', 24
        else:
            return '∉', 'VAR'
    elif cur.value == 26:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == ':':
            return '∈', 'pCOLON'
        else:
            return '∉', 'VAR'
    elif cur.value == 27:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_bcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'a':
            return '∈', 32
        else:
            return '∉', 'VAR'
    elif cur.value == 28:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdfghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'e':
            return '∈', 27
        else:
            return '∉', 'VAR'
    elif cur.value == 29:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdfghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'e':
            return '∈', 30
        else:
            return '∉', 'VAR'
    elif cur.value == 30:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnoqrstuvwxyz':
            return '∈', 3
        elif old.value == 'p':
            return '∈', 28
        else:
            return '∉', 'VAR'
    elif cur.value == 31:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        else:
            return '∉', 'repeat'
    elif cur.value == 32:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrsuvwxyz':
            return '∈', 3
        elif old.value == 't':
            return '∈', 31
        else:
            return '∉', 'VAR'
    elif cur.value == 33:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdfghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'e':
            return '∈', 37
        else:
            return '∉', 'VAR'
    elif cur.value == 34:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghjklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'i':
            return '∈', 36
        else:
            return '∉', 'VAR'
    elif cur.value == 35:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'n':
            return '∈', 39
        else:
            return '∉', 'VAR'
    elif cur.value == 36:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnpqrstuvwxyz':
            return '∈', 3
        elif old.value == 'o':
            return '∈', 35
        else:
            return '∉', 'VAR'
    elif cur.value == 37:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqstuvwxyz':
            return '∈', 3
        elif old.value == 'r':
            return '∈', 38
        else:
            return '∉', 'VAR'
    elif cur.value == 38:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrtuvwxyz':
            return '∈', 3
        elif old.value == 's':
            return '∈', 34
        else:
            return '∉', 'VAR'
    elif cur.value == 39:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == ':':
            return '∈', 'versionCOLON'
        else:
            return '∉', 'VAR'
    elif cur.value == 40:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_bcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'a':
            return '∈', 41
        else:
            return '∉', 'VAR'
    elif cur.value == 41:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abdefghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'c':
            return '∈', 42
        else:
            return '∉', 'VAR'
    elif cur.value == 42:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdfghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'e':
            return '∈', 49
        else:
            return '∉', 'VAR'
    elif cur.value == 43:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdfghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'e':
            return '∈', 47
        else:
            return '∉', 'VAR'
    elif cur.value == 44:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefgijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'h':
            return '∈', 45
        else:
            return '∉', 'VAR'
    elif cur.value == 45:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghjklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == 'i':
            return '∈', 48
        else:
            return '∉', 'VAR'
    elif cur.value == 46:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnoqrstuvwxyz':
            return '∈', 3
        elif old.value == 'p':
            return '∈', 40
        else:
            return '∉', 'VAR'
    elif cur.value == 47:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrtuvwxyz':
            return '∈', 3
        elif old.value == 's':
            return '∈', 46
        else:
            return '∉', 'VAR'
    elif cur.value == 48:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrsuvwxyz':
            return '∈', 3
        elif old.value == 't':
            return '∈', 43
        else:
            return '∉', 'VAR'
    elif cur.value == 49:
        if old.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 3
        elif old.value == ':':
            return '∈', 'whitespaceCOLON'
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
