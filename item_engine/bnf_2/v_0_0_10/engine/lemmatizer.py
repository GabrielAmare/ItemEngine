from collections import deque
from item_engine import CASE
from item_engine.textbase.items.lemmas import Lemma
from item_engine.textbase.items.tokens import Token
from typing import Deque, Dict, Iterator, List, Set, Union


__all__ = ['lemmatizer']


def lemmatizer_propagator(cur: Lemma, old: Token) -> Iterator[CASE]:
    if cur.value == 0:
        if old.value == 'LB':
            yield '∈', 26
        elif old.value == 'LP':
            yield '∈', 28
        elif old.value == 'LS':
            yield '∈', 47
        elif old.value in ('O_Enum', 'O_EnumP', 'O_Match', 'O_MatchAs', 'O_MatchIn', 'O_Optional', 'O_Repeat'):
            yield 'in:args', 18
        elif old.value == 'PLUS':
            yield '∈', 39
        elif old.value in ('P_Inv', 'P_Optional', 'P_Repeat', 'P_RepeatP', 'Var'):
            yield 'in:args', 34
        elif old.value == 'STR':
            yield 'as:expr', 'Str'
        elif old.value == 'Str':
            yield 'as:separator', 46
            yield 'in:args', 44
        elif old.value == 'VAR':
            yield 'as:name', 'Var'
        elif old.value == 'cCOLON':
            yield '∈', 3
        elif old.value == 'gCOLON':
            yield '∈', 13
        elif old.value == 'langCOLON':
            yield '∈', 6
        elif old.value == 'not':
            yield '∈', 36
        elif old.value == 'oCOLON':
            yield '∈', 32
        elif old.value == 'optional':
            yield '∈', 37
        elif old.value == 'pCOLON':
            yield '∈', 42
        elif old.value == 'repeat':
            yield '∈', 38
        else:
            yield '∉', '!Str|Var'
    elif cur.value == 1:
        if old.value == 'EQUAL':
            yield '∈', 2
        else:
            yield '∉', '!Charset'
    elif cur.value == 2:
        if old.value in ('Str', 'Var'):
            yield 'in:args', 4
        else:
            yield '∉', '!Charset'
    elif cur.value == 3:
        if old.value == 'VAR':
            yield 'as:name', 1
        else:
            yield '∉', '!Charset'
    elif cur.value == 4:
        if old.value in ('Str', 'Var'):
            yield 'in:args', 4
        else:
            yield '∉', 'Charset'
    elif cur.value == 5:
        if old.value in ('Charset', 'Group', 'Operator', 'Pattern'):
            yield 'in:args', 11
        else:
            yield '∉', '!Grammar'
    elif cur.value == 6:
        if old.value == 'STR':
            yield 'as:lang', 9
        else:
            yield '∉', '!Grammar'
    elif cur.value == 7:
        if old.value == 'STR':
            yield 'as:version', 10
        else:
            yield '∉', '!Grammar'
    elif cur.value == 8:
        if old.value == 'STR':
            yield 'as:whitespace', 5
        else:
            yield '∉', '!Grammar'
    elif cur.value == 9:
        if old.value == 'versionCOLON':
            yield '∈', 7
        else:
            yield '∉', '!Grammar'
    elif cur.value == 10:
        if old.value == 'whitespaceCOLON':
            yield '∈', 8
        else:
            yield '∉', '!Grammar'
    elif cur.value == 11:
        if old.value in ('Charset', 'Group', 'Operator', 'Pattern'):
            yield 'in:args', 11
        else:
            yield '∉', 'Grammar'
    elif cur.value == 12:
        if old.value == 'EQUAL':
            yield '∈', 14
        else:
            yield '∉', '!Group'
    elif cur.value == 13:
        if old.value == 'VAR':
            yield 'as:name', 12
        else:
            yield '∉', '!Group'
    elif cur.value == 14:
        if old.value == 'VAR':
            yield 'in:names', 16
        else:
            yield '∉', '!Group'
    elif cur.value == 15:
        if old.value == 'VAR':
            yield 'in:names', 17
        else:
            yield '∉', '!Group'
    elif cur.value == 16:
        if old.value == 'VBAR':
            yield '∈', 15
        else:
            yield '∉', '!Group'
    elif cur.value == 17:
        if old.value == 'VBAR':
            yield '∈', 15
        else:
            yield '∉', 'Group'
    elif cur.value == 18:
        if old.value in ('O_Enum', 'O_EnumP', 'O_Match', 'O_MatchAs', 'O_MatchIn', 'O_Optional', 'O_Repeat', 'Str'):
            yield 'in:args', 19
        else:
            yield '∉', '!O_All'
    elif cur.value == 19:
        if old.value in ('O_Enum', 'O_EnumP', 'O_Match', 'O_MatchAs', 'O_MatchIn', 'O_Optional', 'O_Repeat', 'Str'):
            yield 'in:args', 19
        else:
            yield '∉', 'O_All'
    elif cur.value == 20:
        if old.value == 'O_MatchIn':
            yield 'as:child', 'O_Enum'
        else:
            yield '∉', '!O_Enum'
    elif cur.value == 21:
        if old.value == 'O_MatchIn':
            yield 'as:child', 'O_EnumP'
        else:
            yield '∉', '!O_EnumP'
    elif cur.value == 22:
        if old.value == 'VAR':
            yield 'as:key', 23
        else:
            yield '∉', '!O_MatchAs'
    elif cur.value == 23:
        if old.value == 'RS':
            yield '∈', 'O_MatchAs'
        else:
            yield '∉', '!O_MatchAs'
    elif cur.value == 24:
        if old.value == 'VAR':
            yield 'as:key', 25
        else:
            yield '∉', '!O_MatchIn'
    elif cur.value == 25:
        if old.value == 'RS':
            yield '∈', 'O_MatchIn'
        else:
            yield '∉', '!O_MatchIn'
    elif cur.value == 26:
        if old.value == 'O_Any_':
            yield 'as:child', 27
        else:
            yield '∉', '!O_Optional'
    elif cur.value == 27:
        if old.value == 'RB':
            yield '∈', 'O_Optional'
        else:
            yield '∉', '!O_Optional'
    elif cur.value == 28:
        if old.value == 'O_Any_':
            yield 'as:child', 29
        else:
            yield '∉', '!O_Repeat'
    elif cur.value == 29:
        if old.value == 'RP':
            yield '∈', 'O_Repeat'
        else:
            yield '∉', '!O_Repeat'
    elif cur.value == 30:
        if old.value == 'EQUAL':
            yield '∈', 31
        else:
            yield '∉', '!Operator'
    elif cur.value == 31:
        if old.value in ('O_All', 'O_Enum', 'O_EnumP', 'O_Match', 'O_MatchAs', 'O_MatchIn', 'O_Optional', 'O_Repeat', 'Str'):
            yield 'in:args', 33
        else:
            yield '∉', '!Operator'
    elif cur.value == 32:
        if old.value == 'VAR':
            yield 'as:name', 30
        else:
            yield '∉', '!Operator'
    elif cur.value == 33:
        if old.value == 'VBAR':
            yield '∈', 31
        else:
            yield '∉', 'Operator'
    elif cur.value == 34:
        if old.value in ('P_Inv', 'P_Optional', 'P_Repeat', 'P_RepeatP', 'Str', 'Var'):
            yield 'in:args', 35
        else:
            yield '∉', '!P_All'
    elif cur.value == 35:
        if old.value in ('P_Inv', 'P_Optional', 'P_Repeat', 'P_RepeatP', 'Str', 'Var'):
            yield 'in:args', 35
        else:
            yield '∉', 'P_All'
    elif cur.value == 36:
        if old.value == 'Var':
            yield 'as:arg', 'P_Inv'
        else:
            yield '∉', '!P_Inv'
    elif cur.value == 37:
        if old.value in ('P_Inv', 'Str', 'Var'):
            yield 'as:arg', 'P_Optional'
        else:
            yield '∉', '!P_Optional'
    elif cur.value == 38:
        if old.value in ('P_Inv', 'Str', 'Var'):
            yield 'as:arg', 'P_Repeat'
        else:
            yield '∉', '!P_Repeat'
    elif cur.value == 39:
        if old.value in ('P_Inv', 'Str', 'Var'):
            yield 'as:arg', 'P_RepeatP'
        else:
            yield '∉', '!P_RepeatP'
    elif cur.value == 40:
        if old.value == 'EQUAL':
            yield '∈', 41
        else:
            yield '∉', '!Pattern'
    elif cur.value == 41:
        if old.value in ('P_All', 'P_Inv', 'P_Optional', 'P_Repeat', 'P_RepeatP', 'Str', 'Var'):
            yield 'in:args', 43
        else:
            yield '∉', '!Pattern'
    elif cur.value == 42:
        if old.value == 'VAR':
            yield 'as:name', 40
        else:
            yield '∉', '!Pattern'
    elif cur.value == 43:
        if old.value == 'VBAR':
            yield '∈', 41
        else:
            yield '∉', 'Pattern'
    elif cur.value == 44:
        if old.value in ('O_Enum', 'O_EnumP', 'O_Match', 'O_MatchAs', 'O_MatchIn', 'O_Optional', 'O_Repeat'):
            yield 'in:args', 19
        elif old.value in ('P_Inv', 'P_Optional', 'P_Repeat', 'P_RepeatP', 'Var'):
            yield 'in:args', 35
        elif old.value == 'Str':
            yield 'in:args', 45
        else:
            yield '∉', '!O_All|P_All'
    elif cur.value == 45:
        if old.value in ('O_Enum', 'O_EnumP', 'O_Match', 'O_MatchAs', 'O_MatchIn', 'O_Optional', 'O_Repeat'):
            yield 'in:args', 19
        elif old.value in ('P_Inv', 'P_Optional', 'P_Repeat', 'P_RepeatP', 'Var'):
            yield 'in:args', 35
        elif old.value == 'Str':
            yield 'in:args', 45
        else:
            yield '∉', 'P_All'
            yield '∉', 'O_All'
    elif cur.value == 46:
        if old.value == 'DOT':
            yield '∈', 20
        elif old.value == 'HAT':
            yield '∈', 21
        else:
            yield '∉', '!O_Enum|O_EnumP'
    elif cur.value == 47:
        if old.value == 'VAR':
            yield 'as:name', 48
        else:
            yield '∉', '!O_Match|O_MatchAs|O_MatchIn'
    elif cur.value == 48:
        if old.value == 'RS':
            yield '∈', 'O_Match'
        elif old.value == 'as':
            yield '∈', 22
        elif old.value == 'in':
            yield '∈', 24
        else:
            yield '∉', '!O_Match|O_MatchAs|O_MatchIn'
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
