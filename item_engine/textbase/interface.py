from item_engine.textbase import *

lexer, kws, sym = MakeLexer(
    keywords=['operator', 'INF'],
    symbols=['=', '!', '*', '+', '[', ']', '}', '{', '(', ')', '&', '|', ','],
    branches={
        "INT": digits.repeat(1, INF),
        "VAR": charset("ABCDEFGHIJKLMNOPQRSTUVWXYZ_").inc().repeat(1, INF),
        "PROP": charset("abcdefghijklmnopqrstuvwxyz").inc().repeat(1, INF),
        "STR": dq & n_dq.repeat(1, INF) & dq
               | sq & n_sq.repeat(1, INF) & sq,
        "WHITESPACE": charset(" ").inc().repeat(1, INF),
    },
    raw_branches=[
        # Branch("ERROR", CharG.always().inc().repeat(1, INF), -1)
    ]
)

grp = GroupMaker(dict(
    Unit=["__MATCHAS__", "__MATCHIN__", "__LITERAL__", "__GROUP__", "__LOOP__"],
    Bound=["INT", "KW_INF"],
    InGroup=["__ALL__", "Component"]
))

parser, operators = MakeParser(
    operators=dict(
        Var=UNIT(n="VAR", k="name", t=str),
        Prop=UNIT(n="PROP", k="name", t=str),
        Str=UNIT(n="STR", k="expr", t=str),

        MatchAs=OP(sym["{"], grp["VAR"], sym["!"], grp["PROP"], sym["}"]),
        MatchIn=OP(sym["{"], grp["VAR"], sym["*"], grp["PROP"], sym["}"]),
        Literal=OP(grp["STR"]),
        Group=OP(sym['('], grp["InGroup"], sym[')']),
        Loop=OP(grp["Unit"], sym['['], grp['Bound'], sym[','], grp['Bound'], sym[']']),
        And=ENUM(grp["Unit"])
    ),
    branches={

    }
)

engine = Engine(
    name="operator_maker",
    parsers=[
        Parser(
            name='lexer',
            branch_set=lexer,
            input_cls=Char,
            output_cls=Token,
            skips=["WHITESPACE"],
            formal_inputs=True,
            formal_outputs=True,
            reflexive=False
        ),
        Parser(
            name='parser',
            branch_set=parser,
            input_cls=Token,
            output_cls=Lemma,
            skips=[],
            formal_inputs=True,
            formal_outputs=False,
            reflexive=True
        )
    ],
    operators=operators
)

engine.build(root="interface_tests", allow_overwrite=True)

from item_engine.textbase.interface_tests.operator_maker import parse as _parse
from item_engine.textbase.interface_tests.operator_maker.materials import *


def parse(text: str):
    return _parse(make_characters(text, eof=True))


def get(text: str):
    *lemmas, eof = list(parse(text))
    return [build(lemma) for lemma in lemmas if lemma.at == 0 and lemma.to == eof.at]


def operator(expr: str):
    """
    make an operator given a syntax

    ADD:operator = "{TERM !left}" + "{UNIT !right}"
    ADDS:operator = "{UNIT *childs}" & " + {UNIT *childs}"[1, INF]

    :param expr:
    :return:
    """

    return rt_lemmas(parse(expr))


def test(text: str, expected):
    result = get(text)
    assert result == expected, f"\ntext = {text!r}\nexpected = {expected!r}\nresult = {result!r}"


def main():
    test("{TERM !left}", [MatchAs(Var('TERM'), Prop('left'))])
    test("{CHILD *childs}", [MatchIn(Var('CHILD'), Prop('childs'))])
    test("' + '", [Literal(Str("' + '"))])
    test("{TERM !left}' + '{TERM !right}", [And(MatchAs(Var('TERM'), Prop('left')), Literal(Str("' + '")), MatchAs(Var('TERM'), Prop('right')))])
    test("{EXPR !do}' if '{EXPR !if}' else '{EXPR !else}", [And(MatchAs(Var('EXPR'), Prop('do')), Literal(Str("' if '")), MatchAs(Var('EXPR'), Prop('if')), Literal(Str("' else '")), MatchAs(Var('EXPR'), Prop('else')))])

    print(operator("{TERM !left}' + '{UNIT !right}"))
    print(operator("(' + '{UNIT *childs})"))
    print(operator("{UNIT *childs}(' + '{UNIT *childs})[1, INF]"))


if __name__ == '__main__':
    main()
