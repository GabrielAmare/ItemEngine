from item_engine import ACTION, STATE
from item_engine.textbase.items.lemmas import Lemma
from item_engine.textbase.items.tokens import Token
from typing import Dict, Iterator, List, Tuple, Union


__all__ = ['parser']


def _parser(current: Lemma, item: Token) -> Iterator[Tuple[ACTION, STATE]]:
    if current.value == 0:
        if item.value == '(':
            yield 'as:c0', 15
        elif item.value == 'LS':
            yield '∈', 20
        elif item.value == 'STR':
            yield 'as:c0', '__LITERAL__'
        elif item.value == 'VAR':
            yield 'as:c0', 9
        elif item.value == '[':
            yield 'as:c0', 11
        elif item.value in ('__AND__', '__ENUM__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__REPEAT__'):
            yield 'as:c0', 18
        elif item.value == '__LITERAL__':
            yield 'as:c0', 17
        elif item.value == '__OPERATOR__':
            yield 'in:cs', 2
        elif item.value == '__OR__':
            yield 'as:c0', 13
        else:
            yield '∉', '!__AND__|__ENUM__|__GRAMMAR__|__LITERAL__|__MATCHAS__|__MATCHIN__|__MATCH__|__OPERATOR__|__OPTIONAL__|__OR__|__REPEAT__'
    elif current.value == 1:
        if item.value in ('__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__REPEAT__'):
            yield 'as:c1', '__ENUM__'
        else:
            yield '∉', '!__ENUM__'
    elif current.value == 2:
        if item.value == 'NEWLINE':
            yield '∈', 3
        else:
            yield '∉', '!__GRAMMAR__'
    elif current.value == 3:
        if item.value == '__OPERATOR__':
            yield 'in:cs', 4
        else:
            yield '∉', '!__GRAMMAR__'
    elif current.value == 4:
        if item.value == 'NEWLINE':
            yield '∈', 3
        else:
            yield '∉', '__GRAMMAR__'
    elif current.value == 5:
        if item.value == 'VAR':
            yield 'as:c1', 6
        else:
            yield '∉', '!__MATCHAS__'
    elif current.value == 6:
        if item.value == 'RS':
            yield '∈', '__MATCHAS__'
        else:
            yield '∉', '!__MATCHAS__'
    elif current.value == 7:
        if item.value == 'VAR':
            yield 'as:c1', 8
        else:
            yield '∉', '!__MATCHIN__'
    elif current.value == 8:
        if item.value == 'RS':
            yield '∈', '__MATCHIN__'
        else:
            yield '∉', '!__MATCHIN__'
    elif current.value == 9:
        if item.value == 'EQUAL':
            yield '∈', 10
        else:
            yield '∉', '!__OPERATOR__'
    elif current.value == 10:
        if item.value in ('__AND__', '__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__OR__', '__REPEAT__'):
            yield 'as:c1', '__OPERATOR__'
        else:
            yield '∉', '!__OPERATOR__'
    elif current.value == 11:
        if item.value in ('__AND__', '__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__OR__', '__REPEAT__'):
            yield 'as:c1', 12
        else:
            yield '∉', '!__OPTIONAL__'
    elif current.value == 12:
        if item.value == ']':
            yield 'as:c2', '__OPTIONAL__'
        else:
            yield '∉', '!__OPTIONAL__'
    elif current.value == 13:
        if item.value == 'VBAR':
            yield '∈', 14
        else:
            yield '∉', '!__OR__'
    elif current.value == 14:
        if item.value in ('__AND__', '__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__REPEAT__'):
            yield 'as:c1', '__OR__'
        else:
            yield '∉', '!__OR__'
    elif current.value == 15:
        if item.value in ('__AND__', '__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__OR__', '__REPEAT__'):
            yield 'as:c1', 16
        else:
            yield '∉', '!__REPEAT__'
    elif current.value == 16:
        if item.value == ')':
            yield 'as:c2', '__REPEAT__'
        else:
            yield '∉', '!__REPEAT__'
    elif current.value == 17:
        if item.value == 'DOT':
            yield '∈', 1
        elif item.value == 'VBAR':
            yield '∈', 14
        elif item.value in ('__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__REPEAT__'):
            yield 'as:c1', '__AND__'
        else:
            yield '∉', '!__AND__|__ENUM__|__OR__'
    elif current.value == 18:
        if item.value == 'VBAR':
            yield '∈', 14
        elif item.value in ('__ENUM__', '__LITERAL__', '__MATCHAS__', '__MATCHIN__', '__MATCH__', '__OPTIONAL__', '__REPEAT__'):
            yield 'as:c1', '__AND__'
        else:
            yield '∉', '!__AND__|__OR__'
    elif current.value == 19:
        if item.value == 'EXC':
            yield '∈', 5
        elif item.value == 'RS':
            yield '∈', '__MATCH__'
        elif item.value == 'STAR':
            yield '∈', 7
        else:
            yield '∉', '!__MATCHAS__|__MATCHIN__|__MATCH__'
    elif current.value == 20:
        if item.value == 'VAR':
            yield 'as:c0', 19
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
                add_cur(Lemma.after(oldr))
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
                            add_cur(Lemma.after(new))
                            yield new
                            continue
                continue
        if old.value == 'EOF':
            yield Lemma.EOF(old.to)
            break
