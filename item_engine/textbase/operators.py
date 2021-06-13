from typing import Tuple, Union, List, Optional

from item_engine import Group, Match, Branch, All, INF, INCLUDE, INCLUDE_AS as AS_, INCLUDE_IN as IN_, include
from python_generator import LAMBDA, VAR, IF, STR, BLOCK, ARG, SELF, CLASS, METHODS, DEF, AND, EXPRESSION, RETURN, FSTR, \
    ARGS, IMPORT, EQ

from .base_materials import Symbol, Keyword

__all__ = ["UNIT", "OP", "ENUM"]


class UNIT:
    def __init__(self, n: str, k: str, t: type, f: LAMBDA = None):
        assert t in (bool, int, float, str)
        self.n: str = n
        self.k: str = k
        self.t: type = t
        self.f: Optional[LAMBDA] = f

    def pg_if(self, cls_name: str) -> IF:
        PARSE_FUNC = VAR("parse")
        E_CONTENT = VAR("e").GETATTR("content")
        E_VALUE = VAR("e").GETATTR("value")

        if self.f is None:
            prem = []
            arg = E_CONTENT
        else:
            prem = [PARSE_FUNC.ASSIGN(self.f)]
            arg = PARSE_FUNC.CALL(E_CONTENT)

        return IF(
            E_VALUE.EQ(STR(self.n)),
            BLOCK(
                *prem,
                VAR(cls_name).CALL(
                    VAR(self.t.__name__).CALL(arg)
                ).RETURN()
            )
        )

    def pg_class(self, cls_name: str) -> CLASS:
        args = [ARG(k=self.k, t=self.t.__name__)]

        OTHER = VAR("other")

        return CLASS(
            name=cls_name,
            block=[
                METHODS.INIT(*args),
                METHODS.REPR(*args),
                DEF(
                    name="__str__",
                    args=SELF,
                    block=VAR("str").CALL(SELF.GETATTR(self.k)).RETURN()
                ),
                DEF(
                    name="__eq__",
                    args=[SELF, OTHER],
                    block=AND(
                        SELF.TYPE_OF.IS(OTHER.TYPE_OF),
                        SELF.GETATTR(self.k).EQ(OTHER.GETATTR(self.k))
                    ).RETURN()

                )
            ]
        )


class OP:
    def __init__(self, *childs: Union[Group, Symbol, Keyword]):
        self.childs: Tuple[Union[Group, Symbol, Keyword]] = childs

        self.matches: List[Match] = []
        self.args: List[EXPRESSION] = []
        self.as_str: str = ""

        self.n = 0
        for child in self.childs:
            if isinstance(child, (Symbol, Keyword)):
                self.matches.append(Match(child.tokenG, INCLUDE))
                self.as_str += str(child).replace('{', '{{').replace('}', '}}')
            elif isinstance(child, Group):
                self.matches.append(Match(child, AS_.format(f"c{self.n}")))
                self.args.append(VAR("build").CALL(VAR("e").GETATTR("data").GETITEM(STR(f'c{self.n}'))))
                self.as_str += f"{{self.c{self.n}!s}}"
                self.n += 1
            else:
                raise ValueError(child)

    def pg_class(self, cls_name: str):
        keys = [f"c{i}" for i in range(self.n)]
        args = [ARG(key) for key in keys]

        OTHER = VAR("other")

        return CLASS(
            name=cls_name,
            block=[
                METHODS.INIT(*args),
                METHODS.REPR(*args),
                DEF(
                    name="__str__",
                    args=SELF,
                    block=[
                        RETURN(FSTR(self.as_str))
                    ]
                ),
                DEF(
                    name="__eq__",
                    args=[SELF, OTHER],
                    block=AND(
                        SELF.TYPE_OF.IS(OTHER.TYPE_OF),
                        *[SELF.GETATTR(key).EQ(OTHER.GETATTR(key)) for key in keys]
                    ).RETURN()

                )
            ]
        )

    def pg_if(self, cls_name: str):
        br_name = f"__{cls_name.upper()}__"
        return IF(
            VAR("e").GETATTR("value").EQ(STR(br_name)),
            VAR(cls_name).CALL(*self.args).RETURN()
        )

    def branch(self, cls_name: str):
        br_name = f"__{cls_name.upper()}__"
        return Branch(
            name=br_name,
            rule=All.make(*self.matches),
            priority=0
        )


class ENUM:
    def __init__(self, g: Group, s: Union[Symbol, Keyword] = None):
        self.g: Group = g
        self.s: Optional[Union[Symbol, Keyword]] = s

    def pg_class(self, cls_name: str) -> CLASS:
        OTHER = VAR("other")

        CS = VAR("cs")

        return CLASS(
            name=cls_name,
            block=[
                DEF(
                    name="__init__",
                    args=ARGS(SELF, CS.AS_ARG),
                    block=SELF.SETATTR(CS, CS)
                ),
                DEF(
                    name="__repr__",
                    args=SELF,
                    block=FSTR("{self.__class__.__name__}({', '.join(map(repr, self.cs))})").RETURN()
                ),
                DEF(
                    name="__str__",
                    args=SELF,
                    block=STR("" if self.s is None else str(self.s)).GETATTR("join").CALL(
                        VAR("map").CALL("str", SELF.GETATTR("cs"))
                    ).RETURN()
                ),
                IMPORT.FROM("itertools", "starmap"),
                IMPORT.FROM("operator", "eq"),
                DEF(
                    name="__eq__",
                    args=[SELF, OTHER],
                    block=AND(
                        SELF.TYPE_OF.IS(OTHER.TYPE_OF),
                        VAR("all").CALL(
                            VAR("starmap").CALL(
                                VAR("eq"),
                                VAR("zip").CALL(
                                    SELF.GETATTR("cs"),
                                    OTHER.GETATTR("cs")
                                )
                            )
                        )
                    ).RETURN()
                )
            ]
        )

    def pg_if(self, cls_name: str) -> IF:
        br_name = f"__{cls_name.upper()}__"
        return IF(
            EQ(VAR("e").GETATTR("value"), STR(br_name)),
            VAR(cls_name).CALL(
                VAR("map").CALL("build", VAR("e").GETATTR("data").GETITEM(STR("cs"))).AS_ARG,
            ).RETURN()
        )

    def branch(self, cls_name: str):
        br_name = f"__{cls_name.upper()}__"
        if self.s is None:
            rule = Match(self.g, IN_.format("cs")).repeat(2, INF)
        else:
            rule = Match(self.g, IN_.format("cs")) & (include(self.s.tokenG) & Match(self.g, IN_.format("cs"))).repeat(1, INF)

        return Branch(
            name=br_name,
            rule=rule,
            priority=0
        )
