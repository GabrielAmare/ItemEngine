from typing import Type, List

from python_generator import VAR, DEF, BLOCK, FOR, CONTINUE, LIST, STR, IMPORT, IF, SCOPE

from item_engine import Element


def ignore_values(name: str, element_cls: Type[Element], skips: List[str]) -> SCOPE:
    """
    Given consecutive elements,
    remove the elements where the value correspond to the given ``skips``
    and reassign their span (at, to) normalized to (pos, pos+1)

    :param name: the name of the resulting function
    :param element_cls: the Element subclass of the inputs & outputs stream
    :param skips: the Element values to skip
    """
    assert len(skips) > 0
    SRC = VAR("src")
    CUR = VAR("cur")
    POS = VAR("pos")
    AT = VAR("at")
    TO = VAR("to")

    if len(skips) == 1:
        COND = CUR.GETATTR("value").EQ(STR(skips[0]))
    else:
        COND = CUR.GETATTR("value").IN(LIST(list(map(STR, sorted(skips)))))

    return SCOPE(
        IMPORT.FROM("typing", "Iterator"),
        IMPORT.FROM(element_cls.__module__, element_cls.__name__),
        DEF(
            name=name,
            args=SRC.ARG(t=f"Iterator[{element_cls.__name__}]"),
            t=f"Iterator[{element_cls.__name__}]",
            block=BLOCK(
                POS.ASSIGN(0),
                FOR(
                    args=CUR,
                    iterator=SRC,
                    block=BLOCK(
                        IF(
                            condition=COND,
                            block=CONTINUE
                        ),
                        CUR.METH('replace', AT.ARG(POS), TO.ARG(POS.ADD(1))).YIELD(),
                        POS.IADD(1),
                    )
                )
            )
        )
    )


def main():
    from item_engine.textbase import Token
    from python_generator import PACKAGE, MODULE

    package = PACKAGE('package', MODULE('__init__', SCOPE(
        *ignore_values(
            name='ignore_1',
            element_cls=Token,
            skips=["WHITESPACE"]
        ).statements,
        *ignore_values(
            name='ignore_2',
            element_cls=Token,
            skips=["WHITESPACE", "COMMENT"]
        ).statements
    )))

    for module in package.modules:
        module.simplify_imports()

    print(package)


if __name__ == '__main__':
    main()
