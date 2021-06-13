from tkinter import *
from typing import List

from tklib37 import YScrollFrame

from item_engine.textbase import Token


class Frame(Frame):
    # add method to tkinter.Frame class
    def label(self, **config):
        return Label(self, **config)

    def button(self, **config):
        return Button(self, **config)


__all__ = ["TokenGrid"]

LABEL_CFG = dict(bg='black', fg='white', font=('Consolas', 8), bd=1, relief=RIDGE, padx=4, pady=2)


class BaseTokenGrid(Frame):
    def __init__(self, root, tokens, select_span):
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

        for token in tokens:
            self.add_token(token)

    def set_tokens(self, tokens: List[Token]):
        for row, token in enumerate(tokens):
            self.upd_token(row + 1, token)

        for row in reversed(range(len(tokens) + 1, len(self.rows))):
            self.del_row(row)

    def upd_token(self, row, token):
        if 0 <= row < len(self.rows):
            texts = [
                f"{token._at} -> {token._to}",
                token.value,
                repr(token.content)[1:-1],
            ]
            commands = [
                lambda: self.select_span(token._at, token._to),
                lambda: self.select_span(token._at, token._to),
                lambda: self.select_span(token._at, token._to),
            ]
            for widget, text, command in zip(self.rows[row], texts, commands):
                widget.configure(text=text, command=command)
        elif row == len(self.rows):
            self.add_token(token)
        else:
            raise Exception

    def add_token(self, token: Token):
        self.add_row([
            self.button(
                text=f"{token._at} -> {token._to}",
                command=lambda: self.select_span(token._at, token._to),
                **LABEL_CFG
            ),
            self.button(
                text=token.value,
                command=lambda: self.select_span(token._at, token._to),
                **LABEL_CFG
            ),
            self.button(
                text=repr(token.content)[1:-1],
                command=lambda: self.select_span(token._at, token._to),
                **LABEL_CFG
            )
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


class TokenGrid(YScrollFrame):
    def __init__(self, root, tokens, select_span):
        super().__init__(root)
        self.set_widget(BaseTokenGrid, tokens=tokens, select_span=select_span)

    def set_tokens(self, tokens: List[Token]):
        self.widget.set_tokens(tokens)

    def upd_token(self, row, token):
        self.widget.upd_token(row, token)

    def add_token(self, token: Token):
        self.widget.upd_token(token)

    def del_row(self, row):
        self.widget.del_row(row)

    def set_row(self, row, data):
        self.widget.set_row(row, data)

    def add_row(self, data):
        self.widget.add_row(data)
