from collections import deque
from item_engine import CASE
from item_engine.textbase.items.lemmas import Lemma
from item_engine.textbase.items.tokens import Token
from typing import Deque, Dict, Iterator, List, Set, Union


__all__ = ['lemmatizer']


def lemmatizer_propagator(cur: Lemma, old: Token) -> Iterator[CASE]:
    if cur.value == 0:
        if old.value == 'All':
            yield 'in:args', 3
        elif old.value in ('Enum', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat'):
            yield 'in:args', 22
        elif old.value in ('Group', 'Operator'):
            yield 'in:branches', 7
        elif old.value == 'LB':
            yield '∈', 18
        elif old.value == 'LP':
            yield '∈', 20
        elif old.value == 'LS':
            yield '∈', 24
        elif old.value == 'STR':
            yield 'as:content', 'Str'
        elif old.value == 'Str':
            yield 'in:args', 22
            yield 'as:separator', 5
        elif old.value == 'VAR':
            yield 'as:name', 23
        else:
            yield '∉', '!All|Any|Enum|Grammar|Group|Match|MatchAs|MatchIn|Operator|Optional|Repeat|Str'
    elif cur.value == 1:
        if old.value in ('Enum', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat', 'Str'):
            yield 'in:args', 1
        else:
            yield '∉', 'All'
    elif cur.value == 2:
        if old.value in ('All', 'Enum', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat', 'Str'):
            yield 'in:args', 4
        else:
            yield '∉', '!Any'
    elif cur.value == 3:
        if old.value == 'VBAR':
            yield '∈', 2
        else:
            yield '∉', '!Any'
    elif cur.value == 4:
        if old.value == 'VBAR':
            yield '∈', 2
        else:
            yield '∉', 'Any'
    elif cur.value == 5:
        if old.value == 'DOT':
            yield '∈', 6
        else:
            yield '∉', '!Enum'
    elif cur.value == 6:
        if old.value == 'MatchIn':
            yield 'as:child', 'Enum'
        else:
            yield '∉', '!Enum'
    elif cur.value == 7:
        if old.value in ('Group', 'Operator'):
            yield 'in:branches', 8
        else:
            yield '∉', '!Grammar'
    elif cur.value == 8:
        if old.value in ('Group', 'Operator'):
            yield 'in:branches', 8
        else:
            yield '∉', 'Grammar'
    elif cur.value == 9:
        if old.value == 'VAR':
            yield 'in:names', 11
        else:
            yield '∉', '!Group'
    elif cur.value == 10:
        if old.value == 'VAR':
            yield 'in:names', 12
        else:
            yield '∉', '!Group'
    elif cur.value == 11:
        if old.value == 'VBAR':
            yield '∈', 10
        else:
            yield '∉', '!Group'
    elif cur.value == 12:
        if old.value == 'VBAR':
            yield '∈', 10
        else:
            yield '∉', 'Group'
    elif cur.value == 13:
        if old.value == 'VAR':
            yield 'as:key', 14
        else:
            yield '∉', '!MatchAs'
    elif cur.value == 14:
        if old.value == 'RS':
            yield '∈', 'MatchAs'
        else:
            yield '∉', '!MatchAs'
    elif cur.value == 15:
        if old.value == 'VAR':
            yield 'as:key', 16
        else:
            yield '∉', '!MatchIn'
    elif cur.value == 16:
        if old.value == 'RS':
            yield '∈', 'MatchIn'
        else:
            yield '∉', '!MatchIn'
    elif cur.value == 17:
        if old.value in ('All', 'Any', 'Enum', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat', 'Str'):
            yield 'as:rule', 'Operator'
        else:
            yield '∉', '!Operator'
    elif cur.value == 18:
        if old.value in ('All', 'Any', 'Enum', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat', 'Str'):
            yield 'as:child', 19
        else:
            yield '∉', '!Optional'
    elif cur.value == 19:
        if old.value == 'RB':
            yield '∈', 'Optional'
        else:
            yield '∉', '!Optional'
    elif cur.value == 20:
        if old.value in ('All', 'Any', 'Enum', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat', 'Str'):
            yield 'as:child', 21
        else:
            yield '∉', '!Repeat'
    elif cur.value == 21:
        if old.value == 'RP':
            yield '∈', 'Repeat'
        else:
            yield '∉', '!Repeat'
    elif cur.value == 22:
        if old.value in ('Enum', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat', 'Str'):
            yield 'in:args', 1
        elif old.value == 'VBAR':
            yield '∈', 2
        else:
            yield '∉', '!All|Any'
    elif cur.value == 23:
        if old.value == 'EQUAL':
            yield '∈', 17
        elif old.value == 'RV':
            yield '∈', 9
        else:
            yield '∉', '!Group|Operator'
    elif cur.value == 24:
        if old.value == 'VAR':
            yield 'as:name', 25
        else:
            yield '∉', '!Match|MatchAs|MatchIn'
    elif cur.value == 25:
        if old.value == 'EXC':
            yield '∈', 13
        elif old.value == 'RS':
            yield '∈', 'Match'
        elif old.value == 'STAR':
            yield '∈', 15
        else:
            yield '∉', '!Match|MatchAs|MatchIn'
    else:
        raise Exception(f'value = {cur.value!r}')


def lemmatizer_generator(src: Iterator[Token]) -> Iterator[Lemma]:
    eof: int = 0
    queue: Deque[Union[Token, Lemma]] = deque()
    non_terminals: Dict[int, List[Lemma]] = {}
    terminals: List[Lemma] = []
    outputs: List[Lemma] = []
    new_ends: Set[int] = set()
    def add_terminal(e: Lemma):
        if e not in terminals:
            terminals.append(e)
            queue.append(e)
            outputs.append(e)
            new_ends.add(e.to)
    
    def add_non_terminal(e: Lemma):
        if e.to not in non_terminals:
            non_terminals[e.to] = [e]
            new_ends.add(e.to)
        elif e not in non_terminals[e.to]:
            non_terminals[e.to].append(e)
            new_ends.add(e.to)
    
    def add_cursor(at: int):
        add_non_terminal(Lemma.cursor(at))
    
    def get_non_terminals(at: int):
        if at in non_terminals:
            yield from non_terminals[at]
    
    add_cursor(0)
    for inp in src:
        eof: int = inp.to
        queue.append(inp)
        while queue:
            old: Union[Token, Lemma] = queue.popleft()
            for cur in get_non_terminals(old.at):
                for case in lemmatizer_propagator(cur, old):
                    new: Lemma = cur.develop(case, old)
                    if not isinstance(new.value, str):
                        add_non_terminal(new)
                        continue
                    elif not new.value.startswith('!'):
                        add_terminal(new)
                        continue
                    else:
                        continue
            for to in new_ends:
                add_cursor(to)
            new_ends: Set[int] = set()
            if inp.value == 'EOF':
                if outputs:
                    queue.append(inp)
            for output in sorted(outputs, key=lambda out: (out.to, out.at)):
                yield output
            outputs: List[Lemma] = []
    yield Lemma.EOF(at=eof)


def lemmatizer(src: Iterator[Token]) -> Iterator[Lemma]:
    return lemmatizer_generator(src)
