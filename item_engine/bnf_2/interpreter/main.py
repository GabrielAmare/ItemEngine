from item_engine.bnf_2.interpreter import *

import item_engine.bnf.grammar as gr

# from item_engine.textbase.backus_naur_custom.bnf.materials import *
# from item_engine.textbase.backus_naur_custom.bnf import bnc_toplevel


def main(input_file: str = None):
    style = TextStyle({
        'VAR': TagStyle(foreground='#2c68bd'),
        'STR': TagStyle(foreground='#0f9018'),

        'EXC': TagStyle(foreground='#f2a40f'),
        'STAR': TagStyle(foreground='#f2a40f'),
        'COMMENT': TagStyle(foreground='#c9b30a'),
        'ERROR': TagStyle(background='#d91d09'),

        'AS': TagStyle(foreground='#f2a40f'),
        'IN': TagStyle(foreground='#f2a40f'),
        'MATCH': TagStyle(foreground='#f2a40f'),

        'ATlangCOLON': TagStyle(foreground='#c9b30a'),
        'ATversionCOLON': TagStyle(foreground='#c9b30a'),

        'cCOLON': TagStyle(foreground='#5ff514'),
        'pCOLON': TagStyle(foreground='#5ff514'),
        'oCOLON': TagStyle(foreground='#5ff514'),
        'gCOLON': TagStyle(foreground='#5ff514'),

        # 'Charset': TagStyle(background='#26361d'),
        # 'Operator': TagStyle(background='#26361d'),
        # 'Group': TagStyle(background='#26361d'),
        # 'Pattern': TagStyle(background='#26361d'),
    })

    app = App(
        characters=gr.bnf_characters,
        tokenizer=gr.tokenizer,
        lemmatizer=gr.lemmatizer,
        transpiler=bnf_transpiler,
        style=style,
        input_file=input_file
    )
    app.mainloop()


if __name__ == '__main__':
    main()
