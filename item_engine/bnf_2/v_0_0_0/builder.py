from python_generator import PACKAGE

from item_engine import Branch
from item_engine.bnf.constants import SYMBOL_TABLE
from item_engine.textbase import alpha, alphanum, INF, sq, n_sq, dq, n_dq
from .build import EngineBuilder
from .engine import parse, build


def generate(src: str) -> PACKAGE:
    with open(src, mode='r', encoding='utf-8') as file:
        content = file.read()

    grammar = build(parse(content))

    builder = EngineBuilder(
        whitespace=' \t\n',
        type_aliases={
            "VAR": str,
            "STR": str,
        },
        symbol_table=SYMBOL_TABLE
    )

    engine = builder.generate_engine(
        grammar=grammar,
        patterns=[
            Branch(
                name="VAR",
                rule=alpha & alphanum.repeat(0, INF),
                priority=50
            ),
            Branch(
                name="STR",
                rule=sq & n_sq.repeat(0, INF) & sq | dq & n_dq.repeat(0, INF) & dq,
                priority=50
            )
        ]
    )

    package = engine.package

    return package
