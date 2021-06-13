from .lemmatizer import lemmatizer
from .materials import *
from .tokenizer import tokenizer
from item_engine.textbase import Char
from item_engine.textbase.items.lemmas import Lemma
from typing import Iterator, List


def bnf_characters(src: str) -> Iterator[Char]:
    pos: int = -1
    for pos, char in enumerate(src):
        yield Char(at=pos, to=pos + 1, value=char)
    yield Char.EOF(pos + 1)


def bnf_toplevel(src: Iterator[Lemma]) -> Lemma:
    res: List[Lemma] = []
    to: int = 0
    eof: int = 0
    for inp in src:
        if inp.value == 'EOF':
            eof: int = inp.at
            break
        if inp.at == 0:
            if inp.to > to:
                to: int = inp.to
                res: List[Lemma] = [inp]
            elif inp.to == to:
                res.append(inp)
    if len(res) == 1:
        out: Lemma = res[0]
        if out.to == eof:
            return out
        else:
            raise Exception('no complete wrapper element found')
    elif res:
        raise Exception('multiple wrapper elements found')
    else:
        raise Exception('no wrapper element found')


def bnf(src: str) -> Lemma:
    return bnf_toplevel(lemmatizer(tokenizer(bnf_characters(src))))
