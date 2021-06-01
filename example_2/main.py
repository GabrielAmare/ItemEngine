from typing import List

from example_2.spec import engine

engine.build(allow_overwrite=True)

from example_2.engine import parse
from example_2.engine.lexer import lexer
from example_2.engine.parser import parser
from example_2.engine.materials import build

from item_engine.textbase import make_characters, rt_tokens, rt_lemmas, Token

from tools37 import ReprTable, Console

console = Console(show_count=False, show_times=False)


def get(text: str):
    return parse(make_characters(text, eof=True))


def builder(lemmas):
    try:
        *lemmas, eof = lemmas
        return [build(lemma) for lemma in lemmas if lemma.at == 0 and lemma.to == eof.to]
    except:
        return []


# def main():
#     while True:
#         text = input("enter your text : ")
#         if not text:
#             break
#         try:
#             chars = list(make_characters(text, eof=True))
#             tokens = list(lexer(chars))
#             lemmas = list(parser(tokens))
#             builds = list(builder(lemmas))
#
#             content = str(ReprTable([
#                 ['tokens', 'builds', 'lemmas'],
#                 [str(rt_tokens(tokens)), '\n'.join(map(repr, builds)), str(rt_lemmas(lemmas))]
#             ]))
#
#             console.log(content)
#
#         except Exception as e:
#             console.error(str(e))
#
#
# if __name__ == '__main__':
#     main()

from tkinter import *

FRAME_CFG = dict(bg='black')
LABEL_CFG = dict(bg='black', fg='white', font=('Consolas', 10), bd=1, relief=RIDGE)


class TokenGrid(Frame):
    LABEL_CFG = dict(bg='black', fg='white', font=('Consolas', 10), bd=1, relief=RIDGE, padx=10, pady=4)

    def __init__(self, root, tokens, select_span):
        super().__init__(root, **FRAME_CFG)

        self.select_span = select_span

        self.rows = []

        self.add_row([
            Label(self, text='span', **self.LABEL_CFG),
            Label(self, text='type', **self.LABEL_CFG),
            Label(self, text='content', **self.LABEL_CFG),
        ])

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        for token in tokens:
            self.add_token(token)

    def add_token(self, token):
        span = Button(self, text=f"{token._at} -> {token._to}", **self.LABEL_CFG,
                      command=lambda: self.select_span(token._at, token._to))
        value = Button(self, text=token.value, **self.LABEL_CFG,
                       command=lambda: self.select_span(token._at, token._to))
        content = Button(self, text=repr(token.content)[1:-1], **self.LABEL_CFG,
                         command=lambda: self.select_span(token._at, token._to))
        self.add_row([span, value, content])

    def add_row(self, data):
        row = len(self.rows)
        for col, widget in enumerate(data):
            widget.grid(row=row, column=col, sticky=NSEW)
        self.rows.append(data)
        self.update_idletasks()


from tklib37 import YScrollFrame

X0 = -7
Y0 = 0
WIDTH = 1600
HEIGHT = 837


def geometry(width, height, x0, y0):
    return f"{width}x{height}+{x0}+{y0}"


class TokenGridTopLevel(Toplevel):
    def __init__(self, root, select_span, **kw):
        super().__init__(root, **kw)
        self.title('Tokens')
        self.geometry(geometry(WIDTH // 4, HEIGHT, X0, Y0))
        self.overrideredirect(True)
        self.select_span = select_span

        self.ysf = YScrollFrame(self, **FRAME_CFG)
        self.ysf.pack(side=TOP, fill=BOTH, expand=True)

    def set(self, tokens: List[Token]):
        if self.ysf.widget is not None:
            self.ysf.widget.destroy()

        self.ysf.set_widget(TokenGrid, tokens=tokens, select_span=self.select_span)
        self.ysf.widget.pack(side=TOP, fill=BOTH)


class Display(Frame):
    def __init__(self, root, default_text, set_tokens):
        super().__init__(root, **FRAME_CFG)

        self.left = Frame(self, **FRAME_CFG)
        self.right = Frame(self, **FRAME_CFG)
        self.left.pack(side=LEFT, fill=BOTH, expand=True)
        self.right.pack(side=RIGHT, fill=Y)

        self.text = Text(self.left, bg='white', bd=2, relief=SUNKEN)
        self.builds = Label(self.left, **LABEL_CFG)

        self.set_tokens = set_tokens

        self.lemmas = Label(self.right, **LABEL_CFG)

        self.text.pack(side=TOP, fill=BOTH, expand=True)
        self.builds.pack(side=TOP, fill=X)

        self.lemmas.pack(side=TOP, fill=BOTH, expand=True)

        self.text.bind('<Any-KeyRelease>', self.on_key_release)

        default_text = default_text.strip()
        self.text.insert('1.0', default_text)
        self.set(default_text)

    def on_key_release(self, _):
        text = self.text.get('1.0', END).strip()
        self.set(text)

    def get_cursor(self, index: int) -> str:
        lines = self._text[:index].split('\n')
        row = len(lines)
        col = len(lines[-1]) if row else index
        return f"{row}.{col}"

    def select_span(self, at: int, to: int):
        self.text.tag_remove(SEL, "1.0", END)
        self.text.tag_add(SEL, self.get_cursor(at), self.get_cursor(to))
        self.text.focus_force()

    def set(self, text: str):
        self._text = text
        try:
            chars = list(make_characters(text, eof=True))
            tokens = list(lexer(chars))
            lemmas = list(parser(tokens))
            builds = list(builder(lemmas))

            s_lemmas = str(rt_lemmas(lemmas))
            s_builds = '\n\n'.join(map(str, builds))

            self.builds.config(text=s_builds, fg='lime')

            self.set_tokens(tokens)

            # self.lemmas.config(text=s_lemmas)
        except Exception as e:
            self.builds.config(text=f'syntax error !\n{e!s}', fg='red')


class App(Tk):
    def __init__(self, default_text=''):
        super().__init__()
        self.geometry("800x600")

        self.token_grid = TokenGridTopLevel(self, self.select_span)

        self.widget = Display(self, default_text, self.set_tokens)
        self.widget.pack(side=TOP, fill=BOTH, expand=True)

    def select_span(self, at, to):
        return self.widget.select_span(at, to)

    def set_tokens(self, tokens):
        self.token_grid.set(tokens)

    def update(self):
        if hasattr(self, 'token_grid'):
            print(self.token_grid.geometry())

        self.after(250, self.update)

    def mainloop(self, n=0):
        # self.update()

        super().mainloop()


if __name__ == '__main__':
    from item_engine.graphics import App

    app = App(
        tokenizer=lexer,
        lemmatizer=parser,
        builder=builder,
        default_text="""
Match = "{" {VAR !name} "}"
MatchAs = "{" {VAR !name} " !" {VAR !key} "}"
MatchIn = "{" {VAR !name} " *" {VAR !key} "}"
Literal = {STR !content}
And = {S1 !left} {S2 !right}
Or = {S1 !left} " | " {S2 !right}
Operator = {VAR !name} " = " {S0 !rule}
Grammar = "\\n".{Operator *operators}
""".strip())

    app.mainloop()
