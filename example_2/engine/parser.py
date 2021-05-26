from item_engine import ACTION, STATE
from item_engine.textbase.items.lemmas import Lemma
from item_engine.textbase.items.tokens import Token
from typing import Dict, Iterator, List, Tuple, Union


__all__ = ['parser']


def _parser(current: Lemma, item: Token) -> Iterator[Tuple[ACTION, STATE]]:
    if current.value == 0:
        if item.value == 'LS':
            yield '∈', 16
        elif item.value == 'STR':
            yield 'as:c0', '__LITERAL__'
        elif item.value == 'VAR':
            yield 'as:c0', 8
        elif item.value in ('__AND__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__REPEAT__'):
            yield 'as:c0', 13
        elif item.value == '__LITERAL__':
            yield 'as:c0', 14
        elif item.value == '__OPERATOR__':
            yield 'in:cs', 1
        elif item.value == '__OR__':
            yield 'as:c0', 10
        else:
            yield '∉', '!__AND__|__GRAMMAR__|__LITERAL__|__MATCHAS__|__MATCHIN__|__MATCH__|__OPERATOR__|__OR__|__REPEAT__'
    elif current.value == 1:
        if item.value == 'NEWLINE':
            yield '∈', 2
        else:
            yield '∉', '!__GRAMMAR__'
    elif current.value == 2:
        if item.value == '__OPERATOR__':
            yield 'in:cs', 3
        else:
            yield '∉', '!__GRAMMAR__'
    elif current.value == 3:
        if item.value == 'NEWLINE':
            yield '∈', 2
        else:
            yield '∉', '__GRAMMAR__'
    elif current.value == 4:
        if item.value == 'VAR':
            yield 'as:c1', 5
        else:
            yield '∉', '!__MATCHAS__'
    elif current.value == 5:
        if item.value == 'RS':
            yield '∈', '__MATCHAS__'
        else:
            yield '∉', '!__MATCHAS__'
    elif current.value == 6:
        if item.value == 'VAR':
            yield 'as:c1', 7
        else:
            yield '∉', '!__MATCHIN__'
    elif current.value == 7:
        if item.value == 'RS':
            yield '∈', '__MATCHIN__'
        else:
            yield '∉', '!__MATCHIN__'
    elif current.value == 8:
        if item.value == 'EQUAL':
            yield '∈', 9
        else:
            yield '∉', '!__OPERATOR__'
    elif current.value == 9:
        if item.value in ('__AND__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OR__', '__REPEAT__'):
            yield 'as:c1', '__OPERATOR__'
        else:
            yield '∉', '!__OPERATOR__'
    elif current.value == 10:
        if item.value == 'VBAR':
            yield '∈', 11
        else:
            yield '∉', '!__OR__'
    elif current.value == 11:
        if item.value in ('__AND__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__REPEAT__'):
            yield 'as:c1', '__OR__'
        else:
            yield '∉', '!__OR__'
    elif current.value == 12:
        if item.value in ('__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__REPEAT__'):
            yield 'as:c1', '__REPEAT__'
        else:
            yield '∉', '!__REPEAT__'
    elif current.value == 13:
        if item.value == 'VBAR':
            yield '∈', 11
        elif item.value in ('__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__REPEAT__'):
            yield 'as:c1', '__AND__'
        else:
            yield '∉', '!__AND__|__OR__'
    elif current.value == 14:
        if item.value == 'DOT':
            yield '∈', 12
        elif item.value == 'VBAR':
            yield '∈', 11
        elif item.value in ('__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__REPEAT__'):
            yield 'as:c1', '__AND__'
        else:
            yield '∉', '!__AND__|__OR__|__REPEAT__'
    elif current.value == 15:
        if item.value == 'EXC':
            yield '∈', 4
        elif item.value == 'RS':
            yield '∈', '__MATCH__'
        elif item.value == 'STAR':
            yield '∈', 6
        else:
            yield '∉', '!__MATCHAS__|__MATCHIN__|__MATCH__'
    elif current.value == 16:
        if item.value == 'VAR':
            yield 'as:c0', 15
        else:
            yield '∉', '!__MATCHAS__|__MATCHIN__|__MATCH__'
    else:
        raise Exception(f'value = {current.value!r}')


def parser(src: Iterator[Token]) -> Iterator[Lemma]:
    curs: Dict[int, List[Lemma]] = {}
    def add_cur(cur: Lemma):
        to = cur.to
        if to not in curs:
            curs[to] = [cur]
        elif cur not in curs[to]:
            curs[to].append(cur)
    
    add_cur(Lemma(at=0, to=0, value=0))
    stack: List[Union[Token, Lemma]] = []
    j: int = 0
    for old in src:
        stack.append(old)
        while j < len(stack):
            oldr: Lemma = stack[j]
            j += 1
            if oldr.at in curs:
                queue = curs[oldr.at]
                add_cur(Lemma(at=oldr.at, to=oldr.at, value=0))
                i = 0
                while i < len(queue):
                    cur: Lemma = queue[i]
                    i += 1
                    for new in (cur.develop(res, oldr) for res in _parser(cur, oldr)):
                        if not new.is_terminal:
                            add_cur(new)
                            continue
                        if new.is_valid:
                            if new not in stack:
                                stack.insert(j, new)
                            add_cur(Lemma(at=new.to, to=new.to, value=0))
                            yield new
                            continue
                continue
        if old.value == 'EOF':
            yield Lemma.EOF(old.to)
            break
