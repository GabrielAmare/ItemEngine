from collections import deque
from item_engine import ACTION, INDEX, STATE
from item_engine.textbase.items.lemmas import Lemma
from item_engine.textbase.items.tokens import Token
from typing import Callable, Deque, Dict, Iterator, List, Tuple, TypeVar, Union


__all__ = ['parser']


def parser_propagator(current: Lemma, item: Token) -> Iterator[Tuple[ACTION, STATE]]:
    if current.value == 0:
        if item.value == 'LB':
            yield '∈', 13
        elif item.value == 'LP':
            yield '∈', 17
        elif item.value == 'LS':
            yield '∈', 23
        elif item.value == 'STR':
            yield 'as:c0', '__LITERAL__'
        elif item.value == 'VAR':
            yield 'as:c0', 21
            yield 'in:cs', 5
        elif item.value in ('__AND__', '__ENUM__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__REPEAT__'):
            yield 'as:c0', 20
        elif item.value in ('__GROUP__', '__OPERATOR__'):
            yield 'in:cs', 2
        elif item.value == '__LITERAL__':
            yield 'as:c0', 19
        elif item.value == '__OR__':
            yield 'as:c0', 15
        else:
            yield '∉', '!__AND__|__ENUM__|__GRAMMAR__|__GROUPENUM__|__GROUP__|__LITERAL__|__MATCHAS__|__MATCHIN__|__MATCH__|__OPERATOR__|__OPTIONAL__|__OR__|__REPEAT__'
    elif current.value == 1:
        if item.value in ('__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__REPEAT__'):
            yield 'as:c1', '__ENUM__'
        else:
            yield '∉', '!__ENUM__'
    elif current.value == 2:
        if item.value in ('__GROUP__', '__OPERATOR__'):
            yield 'in:cs', 3
        else:
            yield '∉', '!__GRAMMAR__'
    elif current.value == 3:
        if item.value in ('__GROUP__', '__OPERATOR__'):
            yield 'in:cs', 3
        else:
            yield '∉', '__GRAMMAR__'
    elif current.value == 4:
        if item.value == 'VAR':
            yield 'in:cs', 6
        else:
            yield '∉', '!__GROUPENUM__'
    elif current.value == 5:
        if item.value == 'VBAR':
            yield '∈', 4
        else:
            yield '∉', '!__GROUPENUM__'
    elif current.value == 6:
        if item.value == 'VBAR':
            yield '∈', 4
        else:
            yield '∉', '__GROUPENUM__'
    elif current.value == 7:
        if item.value == '__GROUPENUM__':
            yield 'as:c1', '__GROUP__'
        else:
            yield '∉', '!__GROUP__'
    elif current.value == 8:
        if item.value == 'VAR':
            yield 'as:c1', 9
        else:
            yield '∉', '!__MATCHAS__'
    elif current.value == 9:
        if item.value == 'RS':
            yield '∈', '__MATCHAS__'
        else:
            yield '∉', '!__MATCHAS__'
    elif current.value == 10:
        if item.value == 'VAR':
            yield 'as:c1', 11
        else:
            yield '∉', '!__MATCHIN__'
    elif current.value == 11:
        if item.value == 'RS':
            yield '∈', '__MATCHIN__'
        else:
            yield '∉', '!__MATCHIN__'
    elif current.value == 12:
        if item.value in ('__AND__', '__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__OR__', '__REPEAT__'):
            yield 'as:c1', '__OPERATOR__'
        else:
            yield '∉', '!__OPERATOR__'
    elif current.value == 13:
        if item.value in ('__AND__', '__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__OR__', '__REPEAT__'):
            yield 'as:c0', 14
        else:
            yield '∉', '!__OPTIONAL__'
    elif current.value == 14:
        if item.value == 'RB':
            yield '∈', '__OPTIONAL__'
        else:
            yield '∉', '!__OPTIONAL__'
    elif current.value == 15:
        if item.value == 'VBAR':
            yield '∈', 16
        else:
            yield '∉', '!__OR__'
    elif current.value == 16:
        if item.value in ('__AND__', '__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__REPEAT__'):
            yield 'as:c1', '__OR__'
        else:
            yield '∉', '!__OR__'
    elif current.value == 17:
        if item.value in ('__AND__', '__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__OR__', '__REPEAT__'):
            yield 'as:c0', 18
        else:
            yield '∉', '!__REPEAT__'
    elif current.value == 18:
        if item.value == 'RP':
            yield '∈', '__REPEAT__'
        else:
            yield '∉', '!__REPEAT__'
    elif current.value == 19:
        if item.value == 'DOT':
            yield '∈', 1
        elif item.value == 'VBAR':
            yield '∈', 16
        elif item.value in ('__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__REPEAT__'):
            yield 'as:c1', '__AND__'
        else:
            yield '∉', '!__AND__|__ENUM__|__OR__'
    elif current.value == 20:
        if item.value == 'VBAR':
            yield '∈', 16
        elif item.value in ('__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__REPEAT__'):
            yield 'as:c1', '__AND__'
        else:
            yield '∉', '!__AND__|__OR__'
    elif current.value == 21:
        if item.value == 'EQUAL':
            yield '∈', 12
        elif item.value == 'RV':
            yield '∈', 7
        else:
            yield '∉', '!__GROUP__|__OPERATOR__'
    elif current.value == 22:
        if item.value == 'EXC':
            yield '∈', 8
        elif item.value == 'RS':
            yield '∈', '__MATCH__'
        elif item.value == 'STAR':
            yield '∈', 10
        else:
            yield '∉', '!__MATCHAS__|__MATCHIN__|__MATCH__'
    elif current.value == 23:
        if item.value == 'VAR':
            yield 'as:c0', 22
        else:
            yield '∉', '!__MATCHAS__|__MATCHIN__|__MATCH__'
    else:
        raise Exception(f'value = {current.value!r}')


def parser_generator(src: Iterator[Token]) -> Iterator[Lemma]:
    K = TypeVar('K')
    V = TypeVar('V')
    def dict_append(data: Dict[K, List[V]], key: K, val: V):
        if key not in data:
            data[key] = [val]
        elif val not in data[key]:
            data[key].append(val)
    
    def keep_key(data: Dict[K, V], func: Callable[[Iterator[K]], K]) -> Dict[K, V]:
        if not data:
            return data
        key = func(data)
        return {key: data[key]}
    
    c_at: int = 0
    curs: Dict[INDEX, List[Lemma]] = {}
    queue: Deque[Union[Token, Lemma]] = deque()
    for old in src:
        # SRC_ITER
        queue.append(old)
        data0: Dict[INDEX, Dict[INDEX, List[Lemma]]] = {}
        while queue:
            old = queue.popleft()
            old_at = old.at
            dict_append(curs, old_at, Lemma.cursor(old_at))
            for cur in curs[old_at]:
                for case in parser_propagator(cur, old):
                    new = cur.develop(case, old)
                    new_to = new.to
                    new_at = new.at
                    if not isinstance(new.value, str):
                        dict_append(curs, new_to, new)
                        continue
                    if new.value.startswith('!'):
                        continue
                    if new_to not in data0:
                        data0[new_to] = {new_at: [new]}
                    else:
                        dict_append(data0[new_to], new_at, new)
                    queue.append(new)
        for new_to in sorted(data0):
            # FLAT_DATA
            data1 = data0[new_to]
            for new_at in sorted(data1):
                yield from data1[new_at]
        c_at = max(c_at, old.to)
        if data0:
            yield Lemma(at=old.to, to=old.to, value='__sep__')
    yield Lemma.EOF(at=c_at)


def parser(src: Iterator[Token]) -> Iterator[Lemma]:
    return parser_generator(src)
