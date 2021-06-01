from item_engine import ACTION, STATE
from item_engine.textbase.items.lemmas import Lemma
from item_engine.textbase.items.tokens import Token
from typing import Dict, Iterator, List, Tuple, Union


__all__ = ['parser']


def _parser(current: Lemma, item: Token) -> Iterator[Tuple[ACTION, STATE]]:
    if current.value == 0:
        if item.value in ('INT', 'VAR'):
            yield 'as:c0', 1
        else:
            yield '∉', '!__ADD__'
    elif current.value == 1:
        if item.value == 'PLUS':
            yield '∈', 2
        else:
            yield '∉', '!__ADD__'
    elif current.value == 2:
        if item.value in ('INT', 'VAR'):
            yield 'as:c1', '__ADD__'
        else:
            yield '∉', '!__ADD__'
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
