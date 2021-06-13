from __future__ import annotations
from typing import Callable, Iterator, List

from item_engine.textbase import Char, Token, Lemma
from .TextView import TextView

__all__ = ["TextAnalyser"]


class TextAnalyser:
    def __init__(self,
                 characters: Callable[[str], Iterator[Char]],
                 tokenizer: Callable[[Iterator[Char]], Iterator[Token]],
                 lemmatizer: Callable[[Iterator[Token]], Iterator[Lemma]],
                 transpiler: Callable[[str], None],
                 view: TextView
                 ):
        self.characters = characters
        self.tokenizer = tokenizer
        self.lemmatizer = lemmatizer
        self.transpiler = transpiler
        self.view = view

    def analyse(self) -> TextAnalyser.Result:
        text: str = self.view.text
        chars: List[Char] = list(self.characters(text))
        tokens: List[Token] = list(self.tokenizer(chars))
        lemmas: List[Lemma] = list(self.lemmatizer(tokens))
        result: TextAnalyser.Result = TextAnalyser.Result(text, chars, tokens, lemmas)
        return result

    def transpile(self):
        self.transpiler(self.view.text)

    class Result:
        def __init__(self, text: str, chars: List[Char], tokens: List[Token], lemmas: List[Lemma]):
            self.text = text
            self.chars = chars
            self.tokens = tokens
            self.lemmas = lemmas

        @property
        def spans(self):
            for token in self.tokens:
                yield token.value, token._at, token._to

            for lemma in self.lemmas:
                yield lemma.value, lemma._at, lemma._to
