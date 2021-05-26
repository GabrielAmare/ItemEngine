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
        '{', '}', '!', '*', '=', '|', '&', '\n', '.'
    ],
    branches={
        "VAR": alpha & alphanum.repeat(0, INF),
        "STR": sq & n_sq.repeat(0, INF) & sq | dq & n_dq.repeat(0, INF) & dq,
        "WHITESPACE": charset(" \t").inc().repeat(1, INF),
        "COMMENT": charset("#").inc() & (~(charset('\n') | CharG({CharI('EOF')}))).inc().repeat(0, INF)
    }
)

S0 = "S0"
S1 = "S1"
S2 = "S2"

grp = GroupMaker({
    S2: ["__LITERAL__", "__MATCH__", "__MATCHAS__", "__MATCHIN__", "__REPEAT__"],

    S1: [S2, "__AND__"],

    S0: [S1, "__OR__"],
})

parser, operators = MakeParser(
    operators={
        # "Var": UNIT("VAR", "name", str),
        # "Str": UNIT("STR", "content", str),

        "Match": OP(sym['{'], grp["VAR"], sym['}']),
        "MatchAs": OP(sym['{'], grp["VAR"], sym['!'], grp['VAR'], sym['}']),
        "MatchIn": OP(sym['{'], grp["VAR"], sym['*'], grp['VAR'], sym['}']),
        "Literal": OP(grp['STR']),

        "And": OP(grp[S1], grp[S2]),
        "Or": OP(grp[S0], sym['|'], grp[S1]),

        "Repeat": OP(grp["__LITERAL__"], sym['.'], grp[S2]),

        "Operator": OP(grp['VAR'], sym['='], grp[S0]),

        "Grammar": ENUM(grp['__OPERATOR__'], sym['\n'])
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
