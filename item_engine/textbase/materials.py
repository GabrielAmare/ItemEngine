from typing import Tuple, List, Dict, Type, Union, Optional, Iterable
from item_engine import BranchSet, Branch, Group, Rule
from .items import *
from .base_materials import *
from .operators import OP, UNIT, ENUM
from python_generator import MODULE, CLASS, EXPRESSION, IMPORT, DEF, ARG, SWITCH, ISINSTANCE, EXCEPTION, BLOCK, SCOPE, \
    STATEMENT

__all__ = [
    "gen_symbols", "gen_keywords", "gen_branches", "gen_operators",
    "GroupMaker", "SymbolMaker",
    "MakeLexer", "MakeParser"
]


class GroupMaker:
    def __init__(self, data: Dict[str, List[str]]):
        self.data: Dict[str, List[str]] = data

    def __getitem__(self, name: str) -> Group:
        if name not in self.data:
            return TokenG.grp([name])

        result: List[str] = []
        todo: List[str] = [name]
        index = 0
        while index < len(todo):
            name = todo[index]
            if name in self.data:
                for val in self.data[name]:
                    if val not in self.data:
                        result.append(val)
                        continue

                    if val not in todo:
                        todo.append(val)

            index += 1

        return TokenG.grp(result)


class SymbolMaker:
    def __init__(self, **names):
        self.names = {v: k for k, v in names.items()}

    def __call__(self, expr: str) -> Symbol:
        ls = len(expr) - len(expr.lstrip(' '))
        rs = len(expr) - len(expr.rstrip(' '))
        expr = expr.strip(' ')
        return Symbol(name="_".join(map(self.names.__getitem__, expr)), expr=expr, ls=ls, rs=rs)


symbol_maker = SymbolMaker(
    EQUAL="=", PLUS="+", DASH="-", STAR="*", SLASH="/", UNSC="_", VBAR="|", AMPS="&",
    SHARP="#", AT="@", HAT="^", PERCENT="%", WAVE="~", CSLASH="\\",
    COMMA=",", DOT=".", EXC="!", INTER="?", COLON=":", SEMICOLON=";",
    LV="<", RV=">", LP="(", RP=")", LB="[", RB="]", LS="{", RS="}", DQ='"', SQ="'",
    DOLLAR="$", EURO="€", POUND="£", NEWLINE='\n',
    POW0="⁰", POW1="¹", POW2="²", POW3="³", POW4="⁴", POW5="⁵", POW6="⁶", POW7="⁷", POW8="⁸", POW9="⁹",
    # Maths Sets Symbols
    FORALL="∀", EXIST="∃", ISIN="∈", NOTIN="∉", NI="∋",
    CAP="∩", CUP="∪", SUB="⊂", SUP="⊃", NSUB="⊄", SUBE="⊆", SUPE="⊇",
    # Maths Logic Symbols
    AND="∧", OR="∨", EQUIV="≡", THERE4="∴", OPLUS="⊕", OTIMES="⊗", PERP="⊥", LOZ="◊",
    # Other Misc Maths Symbols
    PART="∂", EMPTY="∅", NABLA="∇", PROD="∏", SUM="∑", MINUS="−", LOWAST="∗", RADIC="√", SDOT="⋅",
    PROP="∝", INFIN="∞", ANG="∠", INT="∫", SIM="∼", CONG="≅", ASYMP="≈", NE="≠", LE="≤", GE="≥",
)


def gen_symbols(*exprs: str) -> Tuple[List[Branch], Dict[str, Symbol]]:
    branches: List[Branch] = []
    symbols_register: Dict[str, Symbol] = {}
    for symbol in map(symbol_maker, exprs):
        branches.append(symbol.branch)
        symbols_register[symbol.expr] = symbol

    return branches, symbols_register


def gen_keywords(*exprs: str) -> Tuple[List[Branch], Dict[str, Keyword]]:
    branches = []
    keyword_register: Dict[str, Keyword] = {}

    for expr in exprs:
        ls = len(expr) - len(expr.lstrip(' '))
        rs = len(expr) - len(expr.rstrip(' '))
        expr = expr.strip(' ')

        keyword = Keyword(expr=expr, ls=ls, rs=rs)
        branches.append(keyword.branch)
        keyword_register[keyword.name] = keyword

    return branches, keyword_register


def gen_branches(**config) -> List[Branch]:
    return [Branch(name=key, rule=val) for key, val in config.items()]


BLOCK_I = Optional[Union[BLOCK, SCOPE, STATEMENT, Iterable[STATEMENT]]]


def gen_operators(**data: Dict[str, Union[UNIT, OP, ENUM]]) -> Tuple[List[Branch], MODULE]:
    branches: List[Branch] = []

    classes_operators: List[CLASS] = []
    ifs_operators: List[Tuple[EXPRESSION, BLOCK_I]] = []

    classes_units: List[CLASS] = []
    ifs_units: List[Tuple[EXPRESSION, BLOCK_I]] = []

    op_type: Type[Union[OP, UNIT, ENUM]]

    for cls_name, obj in data.items():
        if isinstance(obj, UNIT):
            classes_units.append(obj.pg_class(cls_name))
            if_ = obj.pg_if(cls_name)
            ifs_units.append((if_.condition, if_.block))
        elif isinstance(obj, (OP, ENUM)):
            branches.append(obj.branch(cls_name))
            classes_operators.append(obj.pg_class(cls_name))
            if_ = obj.pg_if(cls_name)
            ifs_operators.append((if_.condition, if_.block))
        else:
            raise ValueError(obj)

    return branches, MODULE("materials", [
        IMPORT.FROM("item_engine.textbase", "*"),
        *classes_units,
        *classes_operators,
        DEF(
            name="build",
            args=ARG('e', t='Element'),
            block=SWITCH(
                [
                    (
                        ISINSTANCE('e', t='Lemma'),
                        SWITCH(ifs_operators, EXCEPTION('e.value').RAISE())
                    ),
                    (
                        ISINSTANCE('e', t='Token'),
                        SWITCH(ifs_units, EXCEPTION('e.value').RAISE())
                    )
                ],
                EXCEPTION('e.value').RAISE()
            )
        )
    ])


def MakeLexer(
        keywords: List[str] = None,
        symbols: List[str] = None,
        branches: Dict[str, Rule] = None,
        raw_branches: List[Branch] = None
):
    if keywords is None:
        keywords = []
    if symbols is None:
        symbols = []
    if branches is None:
        branches = {}
    if raw_branches is None:
        raw_branches = []

    keyword_branches, keyword_register = gen_keywords(*keywords)
    symbols_branches, symbols_register = gen_symbols(*symbols)

    lexer = BranchSet({
        *keyword_branches,
        *symbols_branches,
        *gen_branches(**branches),
        *raw_branches
    })

    return lexer, keyword_register, symbols_register


def MakeParser(
        operators: Dict[str, Union[UNIT, OP, ENUM]] = None,
        branches: Dict[str, Rule] = None
):
    if operators is None:
        operators = {}
    if branches is None:
        branches = {}

    operators_b, op_register = gen_operators(**operators)

    parser = BranchSet(
        *operators_b,
        *gen_branches(
            **branches
        )
    )

    return parser, op_register
