from tkinter import *
from typing import Tuple, List
from .TextStyle import TextStyle

START = '1.0'


class TextView(Text):
    def __init__(self, root, style: TextStyle = None, **cfg):
        super().__init__(root, **cfg)
        self.config(background='black', foreground='white', insertbackground='yellow')
        self.style: TextStyle = style or TextStyle({})

    ####################################################################################################################
    # TEXT
    ####################################################################################################################

    @property
    def text(self):
        return self.get(START, END).strip()

    @text.setter
    def text(self, value):
        del self.text
        self.insert(START, value)

    @text.deleter
    def text(self):
        self.delete(START, END)

    ####################################################################################################################
    # INDEX & CURSOR
    ####################################################################################################################

    def index_to_cursor(self, index: int) -> str:
        lines = self.text[:index].split('\n')
        row = len(lines)
        col = len(lines[-1]) if row else index
        return f"{row}.{col}"

    ####################################################################################################################
    # SPAN
    ####################################################################################################################

    def select_span(self, at: int, to: int):
        self.tag_remove(SEL, "1.0", END)
        self.tag_add(SEL, self.index_to_cursor(at), self.index_to_cursor(to))
        self.focus_force()

    ####################################################################################################################
    # STYLE
    ####################################################################################################################

    def apply_styles(self, spans: List[Tuple[str, int, int]]):
        for name in self.style.config:
            self.tag_delete(name)

        for name, at, to in spans:
            self.tag_add(name, self.index_to_cursor(at), self.index_to_cursor(to))
            self.tag_config(name, self.style[name])
