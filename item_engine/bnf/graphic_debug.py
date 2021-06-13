from item_engine.graphics import *

import item_engine.bnf.grammar as gr

app = App(
    tokenizer=gr.tokenizer,
    lemmatizer=gr.lemmatizer,
    builder=None,
    default_text="""""",
    show_lemmas=True)


def main():
    app.mainloop()


if __name__ == '__main__':
    main()
