from typing import Tuple, Union, List, Optional

from .. import Group, Match, Branch, All, INF, INCLUDE
import python_generator as pg

from .base_materials import Symbol, Keyword

__all__ = ["UNIT", "OP", "ENUM"]


class UNIT:
    def __init__(self, n: str, k: str, t: type, f: pg.LAMBDA = None):
        assert t in (bool, int, float, str)
        self.n: str = n
        self.k: str = k
        self.t: type = t
        self.f: Optional[pg.LAMBDA] = f

    def pg_if(self, cls_name: str) -> pg.IF:
        PARSE_FUNC = pg.VAR("parse")
        E_CONTENT = pg.VAR("e").GETATTR("content")
        E_VALUE = pg.VAR("e").GETATTR("value")

        if self.f is None:
            prem = []
            arg = E_CONTENT
        else:
            prem = [PARSE_FUNC.ASSIGN(self.f)]
            arg = PARSE_FUNC.CALL(E_CONTENT)

        return pg.IF(
            E_VALUE.EQ(pg.STR(self.n)),
            pg.BLOCK(
                *prem,
                pg.VAR(cls_name).CALL(
                    pg.VAR(self.t.__name__).CALL(arg)
                ).RETURN()
            )
        )

    def pg_class(self, cls_name: str) -> pg.CLASS:
        args = [pg.ARG(k=self.k, t=self.t.__name__)]

        SELF = pg.SELF
        OTHER = pg.VAR("other")

        return pg.CLASS(
            name=cls_name,
            block=[
                pg.METHODS.INIT(*args),
                pg.METHODS.REPR(*args),
                pg.DEF(
                    name="__str__",
                    args=pg.SELF,
                    block=pg.VAR("str").CALL(SELF.GETATTR(self.k)).RETURN()
                ),
                pg.DEF(
                    name="__eq__",
                    args=[SELF, OTHER],
                    block=pg.AND(
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
        self.args: List[pg.EXPRESSION] = []
        self.as_str: str = ""

        self.n = 0
        for child in self.childs:
            if isinstance(child, (Symbol, Keyword)):
                self.matches.append(Match(child.tokenG, INCLUDE))
                self.as_str += str(child).replace('{', '{{').replace('}', '}}')
            elif isinstance(child, Group):
                self.matches.append(child.as_(f"c{self.n}"))
                self.args.append(pg.VAR("build").CALL(pg.VAR("e").GETATTR("data").GETITEM(pg.STR(f'c{self.n}'))))
                self.as_str += f"{{self.c{self.n}!s}}"
                self.n += 1
            else:
                raise ValueError(child)

    def pg_class(self, cls_name: str):
        keys = [f"c{i}" for i in range(self.n)]
        args = [pg.ARG(key) for key in keys]

        OTHER = pg.VAR("other")

        return pg.CLASS(
            name=cls_name,
            block=[
                pg.METHODS.INIT(*args),
                pg.METHODS.REPR(*args),
                pg.DEF(
                    name="__str__",
                    args=pg.SELF,
                    block=[
                        pg.RETURN(pg.FSTR(self.as_str))
                    ]
                ),
                pg.DEF(
                    name="__eq__",
                    args=[pg.SELF, OTHER],
                    block=pg.AND(
                        pg.SELF.TYPE_OF.IS(OTHER.TYPE_OF),
                        *[pg.SELF.GETATTR(key).EQ(OTHER.GETATTR(key)) for key in keys]
                    ).RETURN()

                )
            ]
        )

    def pg_if(self, cls_name: str):
        br_name = f"__{cls_name.upper()}__"
        return pg.IF(
            pg.VAR("e").GETATTR("value").EQ(pg.STR(br_name)),
            pg.VAR(cls_name).CALL(*self.args).RETURN()
        )

    def branch(self, cls_name: str):
        br_name = f"__{cls_name.upper()}__"
        return Branch(
            name=br_name,
            rule=All(tuple(self.matches)),
            priority=0,
            transfer=False
        )


class ENUM:
    def __init__(self, g: Group, s: Union[Symbol, Keyword]):
        self.g: Group = g
        self.s: Union[Symbol, Keyword] = s

    def pg_class(self, cls_name: str) -> pg.CLASS:
        OTHER = pg.VAR("other")

        CS = pg.VAR("cs")

        return pg.CLASS(
            name=cls_name,
            block=[
                pg.DEF(
                    name="__init__",
                    args=pg.ARGS(pg.SELF, CS.AS_ARG),
                    block=pg.SELF.SETATTR(CS, CS)
                ),
                pg.DEF(
                    name="__repr__",
                    args=pg.SELF,
                    block=pg.FSTR("{self.__class__.__name__}({', '.join(map(repr, self.cs))})").RETURN()
                ),
                pg.DEF(
                    name="__str__",
                    args=pg.SELF,
                    block=pg.STR(str(self.s)).GETATTR("join").CALL(
                        pg.VAR("map").CALL("str", pg.SELF.GETATTR("cs"))
                    ).RETURN()
                ),
                pg.IMPORT.FROM("itertools", "starmap"),
                pg.IMPORT.FROM("operator", "eq"),
                pg.DEF(
                    name="__eq__",
                    args=[pg.SELF, OTHER],
                    block=pg.AND(
                        pg.SELF.TYPE_OF.IS(OTHER.TYPE_OF),
                        pg.VAR("all").CALL(
                            pg.VAR("starmap").CALL(
                                pg.VAR("eq"),
                                pg.VAR("zip").CALL(
                                    pg.SELF.GETATTR("cs"),
                                    OTHER.GETATTR("cs")
                                )
                            )
                        )
                    ).RETURN()
                )
            ]
        )

    def pg_if(self, cls_name: str) -> pg.IF:
        br_name = f"__{cls_name.upper()}__"
        return pg.IF(
            pg.EQ(pg.VAR("e").GETATTR("value"), pg.STR(br_name)),
            pg.VAR(cls_name).CALL(
                pg.VAR("map").CALL("build", pg.VAR("e").GETATTR("data").GETITEM(pg.STR("cs"))).AS_ARG,
            ).RETURN()
        )

    def branch(self, cls_name: str):
        br_name = f"__{cls_name.upper()}__"
        return Branch(
            name=br_name,
            rule=self.g.in_("cs") & (self.s.tokenG.inc() & self.g.in_("cs")).repeat(1, INF),
            priority=0,
            transfer=False
        )
