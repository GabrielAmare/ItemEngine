from item_engine import ACTION, IE_SyntaxError, STATE
from item_engine.textbase.items.chars import Char
from item_engine.textbase.items.tokens import Token
from typing import Iterator, Tuple


__all__ = ['lexer']


def _lexer(current: Token, item: Char) -> Tuple[ACTION, STATE]:
    if current.value == 0:
        if item.value in '\t ':
            return '∈', 5
        elif item.value == '\n':
            return '∈', 'NEWLINE'
        elif item.value == '!':
            return '∈', 'EXC'
        elif item.value == '"':
            return '∈', 2
        elif item.value == '#':
            return '∈', 1
        elif item.value == '&':
            return '∈', 'AMPS'
        elif item.value == "'":
            return '∈', 3
        elif item.value == '*':
            return '∈', 'STAR'
        elif item.value == '.':
            return '∈', 'DOT'
        elif item.value == '=':
            return '∈', 'EQUAL'
        elif item.value in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 4
        elif item.value == '{':
            return '∈', 'LS'
        elif item.value == '|':
            return '∈', 'VBAR'
        elif item.value == '}':
            return '∈', 'RS'
        else:
            return '∉', '!AMPS|DOT|EQUAL|EXC|LS|NEWLINE|RS|STAR|VBAR'
    elif current.value == 1:
        if item.value in '\nEOF':
            return '∉', 'COMMENT'
        else:
            return '∈', 1
    elif current.value == 2:
        if item.value == '"':
            return '∈', 'STR'
        elif item.value == 'EOF':
            return '∉', '!STR'
        else:
            return '∈', 2
    elif current.value == 3:
        if item.value == "'":
            return '∈', 'STR'
        elif item.value == 'EOF':
            return '∉', '!STR'
        else:
            return '∈', 3
    elif current.value == 4:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 4
        else:
            return '∉', 'VAR'
    elif current.value == 5:
        if item.value in '\t ':
            return '∈', 5
        else:
            return '∉', 'WHITESPACE'
    else:
        raise Exception(f'value = {current.value!r}')


def lexer(src: Iterator[Char]) -> Iterator[Token]:
    cur: Token = Token(at=0, to=0, value=0)
    pos: int = 0
    for old in src:
        while cur.to == old.at:
            new: Token = cur.develop(_lexer(cur, old), old)
            if not new.is_terminal:
                cur = new
                continue
            if new.is_valid:
                cur = Token(at=new.to, to=new.to, value=0)
                if new.value in ['WHITESPACE']:
                    continue
                else:
                    new = new.replace(at=pos, to=pos + 1)
                    pos += 1
                yield new
                continue
            if old.value == 'EOF':
                yield Token.EOF(pos)
                break
            raise IE_SyntaxError(cur, old, new)
