"""
    Specification module : contains the definition of the grammar to build,
    this should be changed to update the engine.
    WARNING : DO NOT MODIFY THE ENGINE AS IT WILL BE REGENERATED EACH TIME /!\
"""
from item_engine.textbase import *

__all__ = ['engine']

not_eof = CharG({CharI(char=EOF)}, True).inc()

lexer, kws, sym = MakeLexer(
    keywords=[],
    symbols=[
        ' + ', ' - ', ' / ', ' * ', ' = '
    ],
    branches={
        "VAR": alpha & alphanum.repeat(0, INF),
        "INT": digits.repeat(1, INF),
        "FLOAT": digits.repeat(1, INF) & dot & digits.repeat(0, INF) | dot & digits.repeat(1, INF),
        "WHITESPACE": charset(" \t").inc().repeat(1, INF)
    }
)

grp = GroupMaker({
    "unit": ["VAR", "INT"]
})

parser, operators = MakeParser(
    operators={
        "Var": UNIT(n="VAR", k="name", t=str),
        "Int": UNIT(n="INT", k="value", t=int),

        "Add": OP(grp["unit"], sym['+'], grp['unit'])
    },
    branches={

    }
)

engine = Engine(
    name='engine',
    parsers=[
        Parser(
            name='lexer',
            branch_set=lexer,
            input_cls=Char,
            output_cls=Token,
            group_cls=CharG,
            formal_inputs=True,
            formal_outputs=True,
            reflexive=False,
            skips=["WHITESPACE"]
        ),
        Parser(
            name='parser',
            branch_set=parser,
            input_cls=Token,
            output_cls=Lemma,
            group_cls=TokenG,
            formal_inputs=True,
            formal_outputs=False,
            reflexive=True,
            skips=[]
        )
    ],
    operators=operators
)


def main():
    engine.build(allow_overwrite=True)


if __name__ == '__main__':
    main()
