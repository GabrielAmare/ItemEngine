from collections import deque
from item_engine import ACTION, INDEX, STATE
from item_engine.textbase.items.chars import Char
from item_engine.textbase.items.tokens import Token
from typing import Deque, Dict, Iterator, List, Tuple


__all__ = ['lexer']


def lexer_propagator(current: Token, item: Char) -> Tuple[ACTION, STATE]:
    if current.value == 0:
        if item.value in '\t\n ':
            return '∈', 5
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
        elif item.value == '(':
            return '∈', 'LP'
        elif item.value == ')':
            return '∈', 'RP'
        elif item.value == '*':
            return '∈', 'STAR'
        elif item.value == '.':
            return '∈', 'DOT'
        elif item.value == '=':
            return '∈', 'EQUAL'
        elif item.value == '>':
            return '∈', 'RV'
        elif item.value in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 4
        elif item.value == '[':
            return '∈', 'LB'
        elif item.value == ']':
            return '∈', 'RB'
        elif item.value == '{':
            return '∈', 'LS'
        elif item.value == '|':
            return '∈', 'VBAR'
        elif item.value == '}':
            return '∈', 'RS'
        else:
            return '∉', '!AMPS|DOT|EQUAL|EXC|LB|LP|LS|RB|RP|RS|RV|STAR|VBAR'
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
        if item.value in '\t\n ':
            return '∈', 5
        else:
            return '∉', 'WHITESPACE'
    else:
        raise Exception(f'value = {current.value!r}')


def lexer_generator(src: Iterator[Char]) -> Iterator[Token]:
    curs: Dict[INDEX, List[Token]] = {}
    queue: Deque[Char] = deque()
    eof = 0
    at = 0
    for old in src:
        if old.value == 'EOF':
            eof = old.at
        queue.append(old)
        ctd_out: List[Token] = []
        while queue:
            old = queue.popleft()
            curs.setdefault(old.at, [])
            cursor = Token.cursor(old.at)
            if cursor not in curs[old.at]:
                curs[old.at].append(cursor)
            for cur in curs[old.at]:
                new = cur.develop(lexer_propagator(cur, old), old)
                if isinstance(new.value, str):
                    if new.value.startswith('!'):
                        continue
                    ctd_out.append(new)
                else:
                    curs.setdefault(new.to, [])
                    if new in curs[new.to]:
                        continue
                    curs[new.to].append(new)
        data0: Dict[INDEX, Tuple[INDEX, List[Token]]] = {}
        for new in ctd_out:
            if new.to not in data0:
                data0[new.to] = (new.at, [new])
                continue
            item = data0[new.to]
            at = item[0]
            data1 = item[1]
            if new.at == at:
                data1.append(new)
                continue
            if new.at < at:
                data0[new.to] = (new.at, [new])
                continue
        ctd_out = []
        for to in sorted(data0.keys()):
            for new in data0[to][1]:
                ctd_out.append(new)
        keep = []
        for new in ctd_out:
            if new.at >= at:
                keep.append(new)
        ctd_out = keep
        for new in ctd_out:
            yield new
        if ctd_out:
            yield Token(at=old.to, to=old.to, value='__SEP__')
            at = old.to
    yield Token.EOF(at=eof)


def lexer(src: Iterator[Char]) -> Iterator[Token]:
    return lexer_generator(src)
