from tkinter import *
from typing import List

from tklib37 import YScrollFrame

from item_engine.textbase import Lemma, Token


class Frame(Frame):
    # add method to tkinter.Frame class
    def label(self, **config):
        return Label(self, **config)

    def button(self, **config):
        return Button(self, **config)


__all__ = ["LemmaGrid"]

LABEL_CFG = dict(bg='black', fg='white', font=('Consolas', 8), bd=1, relief=RIDGE, padx=4, pady=2)


class BaseLemmaGrid(Frame):
    def __init__(self, root, lemmas, select_span):
        super().__init__(root, bg='black')

        self.select_span = select_span

        self.rows = []

        self.add_row([
            self.label(text='span', **LABEL_CFG),
            self.label(text='type', **LABEL_CFG),
            self.label(text='content', **LABEL_CFG),
        ])

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        for lemma in lemmas:
            self.add_lemma(lemma)

    @staticmethod
    def get_lemma_content(lemma: Lemma) -> str:
        def get_unit(obj) -> str:
            if isinstance(obj, Lemma):
                return f": {obj.value} = ..."
            elif isinstance(obj, Token):
                return f": {obj.value} = {obj.content!r}"
            else:
                raise TypeError(type(obj))

        lines = []
        for k, v in lemma.data.items():
            if isinstance(v, list):
                for i, e in enumerate(v):
                    lines.append(f"{k}[{i}]{get_unit(e)}")
            else:
                lines.append(f"{k}{get_unit(v)}")

        return '\n'.join(lines)

    def set_lemmas(self, lemmas: List[Lemma]):
        for row, lemma in enumerate(lemmas):
            self.upd_lemma(row + 1, lemma)

        for row in reversed(range(len(lemmas) + 1, len(self.rows))):
            self.del_row(row)

    def get_lemma_configs(self, lemma: Lemma):
        command = lambda: self.select_span(lemma._at, lemma._to)
        yield dict(text=f"{lemma._at} -> {lemma._to}", command=command)
        yield dict(text=lemma.value, command=command)
        yield dict(text=self.get_lemma_content(lemma), command=command)

    def upd_lemma(self, row, lemma):
        if 0 <= row < len(self.rows):
            for widget, config in zip(self.rows[row], self.get_lemma_configs(lemma)):
                widget.configure(**config)

        elif row == len(self.rows):
            self.add_lemma(lemma)
        else:
            raise Exception

    def add_lemma(self, lemma: Lemma):
        self.add_row([
            self.button(**config, **LABEL_CFG)
            for config in self.get_lemma_configs(lemma)
        ])

    def del_row(self, row):
        if 0 <= row < len(self.rows):
            for widget in self.rows[row]:
                widget.destroy()
            del self.rows[row]

    def set_row(self, row, data):
        for col, widget in enumerate(data):
            widget.grid(row=row, column=col, sticky=NSEW)
        self.rows[row] = data

    def add_row(self, data):
        row = len(self.rows)
        for col, widget in enumerate(data):
            widget.grid(row=row, column=col, sticky=NSEW)
        self.rows.append(data)


class LemmaGrid(YScrollFrame):
    def __init__(self, root, lemmas, select_span):
        super().__init__(root)
        self.set_widget(BaseLemmaGrid, lemmas=lemmas, select_span=select_span)

    def set_lemmas(self, lemmas: List[Lemma]):
        self.widget.set_lemmas(lemmas)

    def upd_lemma(self, row, lemma):
        self.widget.upd_lemma(row, lemma)

    def add_lemma(self, lemma: Lemma):
        self.widget.upd_lemma(lemma)

    def del_row(self, row):
        self.widget.del_row(row)

    def set_row(self, row, data):
        self.widget.set_row(row, data)

    def add_row(self, data):
        self.widget.add_row(data)
