from tkinter import *

START = '1.0'

__all__ = ["TextInput"]


class TextInput(Text):
    def __init__(self, root, callback=None, styles: dict = None, **kw):
        super().__init__(root, **kw)
        self.callback = callback
        self.bind('<Any-KeyRelease>', self._on_key_release, add=True)

        self.styles = styles or {}

    def _on_key_release(self, _):
        if self.callback:
            self.callback(self.get_text())

    def set_text(self, text: str) -> None:
        self.del_text()
        self.insert(START, text)

    def get_text(self) -> str:
        return self.get(START, END)[:-1]

    def del_text(self) -> None:
        self.delete(START, END)

    def get_cursor(self, index: int) -> str:
        lines = self.get_text()[:index].split('\n')
        row = len(lines)
        col = len(lines[-1]) if row else index
        return f"{row}.{col}"

    def select_span(self, at: int, to: int):
        self.tag_remove(SEL, "1.0", END)
        self.tag_add(SEL, self.get_cursor(at), self.get_cursor(to))
        self.focus_force()

    def apply_styles(self, spans):
        for name in self.styles:
            self.tag_delete(name)

        for name, at, to in spans:
            if name in self.styles:
                self.tag_add(name, self.get_cursor(at), self.get_cursor(to))
                self.tag_config(name, self.styles.get(name, {}))

