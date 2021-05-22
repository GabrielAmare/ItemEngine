from item_engine import ACTION, STATE
from item_engine.textbase.items.chars import Char
from item_engine.textbase.items.tokens import Token
from typing import Iterator, Tuple


__all__ = ['lexer']


def _lexer(current: Token, item: Char) -> Tuple[ACTION, STATE]:
    if current.value == 0:
        if item.value == '*':
            return '∈', 'STAR'
        elif item.value == '+':
            return '∈', 'PLUS'
        elif item.value == '-':
            return '∈', 'DASH'
        elif item.value == '.':
            return '∈', 1
        elif item.value == '/':
            return '∈', 'SLASH'
        elif item.value in '0123456789':
            return '∈', 2
        elif item.value in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 4
        else:
            return '∉', '!DASH|PLUS|SLASH|STAR'
    elif current.value == 2:
        if item.value == '.':
            return '∈', 3
        elif item.value in '0123456789':
            return '∈', 2
        else:
            return '∉', 'INT'
    elif current.value == 4:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 4
        else:
            return '∉', 'VAR'
    elif current.value == 1:
        if item.value in '0123456789':
            return '∈', 3
        else:
            return '∉', '!FLOAT'
    elif current.value == 3:
        if item.value in '0123456789':
            return '∈', 3
        else:
            return '∉', 'FLOAT'
    else:
        raise Exception(f'value = {current.value!r}')


def lexer(src: Iterator[Char]) -> Iterator[Token]:
    cur: Token = Token(at=0, to=0, value=0)
    for old in src:
        while cur.to == old.at:
            new: Token = cur.develop(_lexer(cur, old), old)
            if not new.is_terminal:
                cur = new
                continue
            if new.is_valid:
                cur = Token(at=new.to, to=new.to, value=0)
                yield new
                continue
            if old.value == 'EOF':
                yield Token.EOF(old.to)
                break
            raise SyntaxError((cur, old, new))
