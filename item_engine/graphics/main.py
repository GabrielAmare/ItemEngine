from tkinter import *
from typing import List

from item_engine.textbase import make_characters, Token, Lemma, Char

from item_engine import INDEX, IE_SyntaxError

from item_engine.graphics.TopLevelWrapper import TopLevelWrapper
from item_engine.graphics.TokenGrid import TokenGrid
from item_engine.graphics.LemmaGrid import LemmaGrid
from item_engine.graphics.TextInput import TextInput

X0 = -7
Y0 = 0
WIDTH = 1600
HEIGHT = 837


def geometry(width, height, x0, y0):
    return f"{width}x{height}+{x0}+{y0}"


class App(Tk):
    def __init__(self, tokenizer=None, lemmatizer=None, builder=None, default_text: str = "",
                 show_lemmas: bool = False):
        super().__init__()
        STYLES = {
            'VAR': dict(foreground='#2c68bd'),
            'STR': dict(foreground='#0f9018'),
            'EXC': dict(foreground='#f2a40f'),
            'STAR': dict(foreground='#f2a40f'),
            'COMMENT': dict(foreground='#c9b30a'),
            'ERROR': dict(background='#d91d09'),

            'AS': dict(foreground='#f2a40f'),
            'IN': dict(foreground='#f2a40f'),
            'MATCH': dict(foreground='#f2a40f'),

            'HOLO_CREATE': dict(foreground='#20e6d2'),
            'HOLO_SCALE': dict(foreground='#20e6d2'),
            'HOLO_COLOR': dict(foreground='#20e6d2'),
            'HOLO_MODEL': dict(foreground='#20e6d2'),
        }
        self.widget = TextInput(self,
                                callback=self._on_text_update,
                                styles=STYLES,
                                bg='black',
                                fg='white',
                                insertbackground='yellow',
                                selectbackground='#202121'
                                )
        self.widget.pack(side=TOP, fill=BOTH, expand=True)

        self.tokenizer = tokenizer
        if show_lemmas:
            self.lemmatizer = lemmatizer
        else:
            self.lemmatizer = None
        self.builder = builder

        self.tl_tokens: TopLevelWrapper = TopLevelWrapper(self, bg='black', bd=0)
        self.tokens: TokenGrid = self.tl_tokens.of(TokenGrid, tokens=[], select_span=self._select_span)

        if show_lemmas:
            self.tl_lemmas: TopLevelWrapper = TopLevelWrapper(self, bg='black', bd=0)
            self.lemmas: LemmaGrid = self.tl_lemmas.of(LemmaGrid, lemmas=[], select_span=self._select_span)

        if show_lemmas:
            SIZE = WIDTH // 3
        else:
            SIZE = WIDTH // 2

        self.tl_tokens.title('TOKENS')
        self.tl_tokens.geometry(geometry(SIZE, HEIGHT, X0, Y0))
        # self.tl_tokens.overrideredirect(1)

        self.title('INPUTS')
        self.geometry(geometry(SIZE, HEIGHT, SIZE + X0, Y0))

        if show_lemmas:
            self.tl_lemmas.title('LEMMAS')
            self.tl_lemmas.geometry(geometry(SIZE, HEIGHT, 2 * SIZE + X0, Y0))
            # self.tl_lemmas.overrideredirect(1)

        self.widget.set_text(default_text)
        self._on_text_update(default_text)

    def _build_tokens(self, characters: List[Char], size: int) -> List[Token]:
        tokens = []
        try:
            for token in self.tokenizer(characters):
                tokens.append(token)
        except IE_SyntaxError as error:
            tokens.append(Token(error.new._at, to=size, value=f'ERROR : {error.new}'))
        return tokens

    def _build_lemmas(self, tokens: List[Token], size: int) -> List[Lemma]:
        lemmas = []
        try:
            for lemma in self.lemmatizer(tokens):
                lemmas.append(lemma)
        except IE_SyntaxError as error:
            lemmas.append(Lemma(error.new._at, to=size, value=f'ERROR : {error.new}'))
        return lemmas

    def _on_text_update(self, text: str):
        size = len(text)
        characters = list(make_characters(text, eof=True))
        spans = []
        if self.tokenizer:
            tokens = self._build_tokens(characters, size)
            self.tokens.set_tokens(tokens)
            spans += [(token.value, token._at, token._to) for token in tokens]

            if self.lemmatizer:
                lemmas = self._build_lemmas(tokens, size)
                self.lemmas.set_lemmas(lemmas)
                spans += [(lemma.value, lemma._at, lemma._to) for lemma in lemmas]

                if self.builder:
                    builds = list(self.builder(lemmas))
                    print(builds)

        self.widget.apply_styles(spans)

    def _select_span(self, at: INDEX, to: INDEX):
        self.widget.select_span(at, to)


if __name__ == '__main__':
    app = App()

    app.mainloop()
