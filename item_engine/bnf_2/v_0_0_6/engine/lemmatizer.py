from collections import deque
from item_engine import CASE
from item_engine.textbase.items.lemmas import Lemma
from item_engine.textbase.items.tokens import Token
from typing import Deque, Dict, Iterator, List, Set, Union


__all__ = ['lemmatizer']


def lemmatizer_propagator(cur: Lemma, old: Token) -> Iterator[CASE]:
    if cur.value == 0:
        if old.value == 'ATlangCOLON':
            yield '∈', 14
        elif old.value == 'All':
            yield 'in:args', 3
        elif old.value in ('Enum', 'EnumP', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat'):
            yield 'in:args', 39
        elif old.value == 'LB':
            yield '∈', 31
        elif old.value == 'LP':
            yield '∈', 37
        elif old.value == 'LS':
            yield '∈', 41
        elif old.value == 'STR':
            yield 'as:expr', 'Str'
        elif old.value == 'Str':
            yield 'in:args', 39
            yield 'as:separator', 40
        elif old.value == 'VAR':
            yield 'as:name', 'Var'
        elif old.value == 'cCOLON':
            yield '∈', 7
        elif old.value == 'gCOLON':
            yield '∈', 19
        elif old.value == 'oCOLON':
            yield '∈', 29
        elif old.value == 'pCOLON':
            yield '∈', 35
        else:
            yield '∉', '!Enum|EnumP|Match|MatchAs|MatchIn|Optional|Repeat|Str'
    elif cur.value == 1:
        if old.value in ('Enum', 'EnumP', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat', 'Str'):
            yield 'in:args', 1
        else:
            yield '∉', 'All'
    elif cur.value == 2:
        if old.value in ('All', 'Enum', 'EnumP', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat', 'Str'):
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
        if old.value == 'EQUAL':
            yield '∈', 6
        else:
            yield '∉', '!Charset'
    elif cur.value == 6:
        if old.value in ('Str', 'Var'):
            yield 'in:args', 8
        else:
            yield '∉', '!Charset'
    elif cur.value == 7:
        if old.value == 'VAR':
            yield 'as:name', 5
        else:
            yield '∉', '!Charset'
    elif cur.value == 8:
        if old.value in ('Str', 'Var'):
            yield 'in:args', 8
        else:
            yield '∉', 'Charset'
    elif cur.value == 9:
        if old.value == 'MatchIn':
            yield 'as:child', 'Enum'
        else:
            yield '∉', '!Enum'
    elif cur.value == 10:
        if old.value == 'MatchIn':
            yield 'as:child', 'EnumP'
        else:
            yield '∉', '!EnumP'
    elif cur.value == 11:
        if old.value == 'ATversionCOLON':
            yield '∈', 15
        else:
            yield '∉', '!Grammar'
    elif cur.value == 12:
        if old.value == 'ATwhitespaceCOLON':
            yield '∈', 16
        else:
            yield '∉', '!Grammar'
    elif cur.value == 13:
        if old.value in ('Charset', 'Group', 'Operator', 'Pattern'):
            yield 'in:args', 17
        else:
            yield '∉', '!Grammar'
    elif cur.value == 14:
        if old.value == 'STR':
            yield 'as:lang', 11
        else:
            yield '∉', '!Grammar'
    elif cur.value == 15:
        if old.value == 'STR':
            yield 'as:version', 12
        else:
            yield '∉', '!Grammar'
    elif cur.value == 16:
        if old.value == 'STR':
            yield 'as:whitespace', 13
        else:
            yield '∉', '!Grammar'
    elif cur.value == 17:
        if old.value in ('Charset', 'Group', 'Operator', 'Pattern'):
            yield 'in:args', 17
        else:
            yield '∉', 'Grammar'
    elif cur.value == 18:
        if old.value == 'EQUAL':
            yield '∈', 20
        else:
            yield '∉', '!Group'
    elif cur.value == 19:
        if old.value == 'VAR':
            yield 'as:name', 18
        else:
            yield '∉', '!Group'
    elif cur.value == 20:
        if old.value == 'VAR':
            yield 'in:names', 22
        else:
            yield '∉', '!Group'
    elif cur.value == 21:
        if old.value == 'VAR':
            yield 'in:names', 23
        else:
            yield '∉', '!Group'
    elif cur.value == 22:
        if old.value == 'VBAR':
            yield '∈', 21
        else:
            yield '∉', '!Group'
    elif cur.value == 23:
        if old.value == 'VBAR':
            yield '∈', 21
        else:
            yield '∉', 'Group'
    elif cur.value == 24:
        if old.value == 'VAR':
            yield 'as:key', 25
        else:
            yield '∉', '!MatchAs'
    elif cur.value == 25:
        if old.value == 'RS':
            yield '∈', 'MatchAs'
        else:
            yield '∉', '!MatchAs'
    elif cur.value == 26:
        if old.value == 'VAR':
            yield 'as:key', 27
        else:
            yield '∉', '!MatchIn'
    elif cur.value == 27:
        if old.value == 'RS':
            yield '∈', 'MatchIn'
        else:
            yield '∉', '!MatchIn'
    elif cur.value == 28:
        if old.value == 'EQUAL':
            yield '∈', 30
        else:
            yield '∉', '!Operator'
    elif cur.value == 29:
        if old.value == 'VAR':
            yield 'as:name', 28
        else:
            yield '∉', '!Operator'
    elif cur.value == 30:
        if old.value in ('All', 'Any', 'Enum', 'EnumP', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat', 'Str'):
            yield 'as:rule', 'Operator'
        else:
            yield '∉', '!Operator'
    elif cur.value == 31:
        if old.value in ('All', 'Any', 'Enum', 'EnumP', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat', 'Str'):
            yield 'as:child', 32
        else:
            yield '∉', '!Optional'
    elif cur.value == 32:
        if old.value == 'RB':
            yield '∈', 'Optional'
        else:
            yield '∉', '!Optional'
    elif cur.value == 33:
        if old.value == 'EQUAL':
            yield '∈', 34
        else:
            yield '∉', '!Pattern'
    elif cur.value == 34:
        if old.value in ('Str', 'Var'):
            yield 'in:args', 36
        else:
            yield '∉', '!Pattern'
    elif cur.value == 35:
        if old.value == 'VAR':
            yield 'as:name', 33
        else:
            yield '∉', '!Pattern'
    elif cur.value == 36:
        if old.value in ('Str', 'Var'):
            yield 'in:args', 36
        else:
            yield '∉', 'Pattern'
    elif cur.value == 37:
        if old.value in ('All', 'Any', 'Enum', 'EnumP', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat', 'Str'):
            yield 'as:child', 38
        else:
            yield '∉', '!Repeat'
    elif cur.value == 38:
        if old.value == 'RP':
            yield '∈', 'Repeat'
        else:
            yield '∉', '!Repeat'
    elif cur.value == 39:
        if old.value in ('Enum', 'EnumP', 'Match', 'MatchAs', 'MatchIn', 'Optional', 'Repeat', 'Str'):
            yield 'in:args', 1
        elif old.value == 'VBAR':
            yield '∈', 2
        else:
            yield '∉', '!All'
    elif cur.value == 40:
        if old.value == 'DOT':
            yield '∈', 9
        elif old.value == 'HAT':
            yield '∈', 10
        else:
            yield '∉', '!Enum|EnumP'
    elif cur.value == 41:
        if old.value == 'VAR':
            yield 'as:name', 42
        else:
            yield '∉', '!Match|MatchAs|MatchIn'
    elif cur.value == 42:
        if old.value == 'EXC':
            yield '∈', 24
        elif old.value == 'RS':
            yield '∈', 'Match'
        elif old.value == 'STAR':
            yield '∈', 26
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
