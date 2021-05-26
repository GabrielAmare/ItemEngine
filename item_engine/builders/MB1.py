from typing import Type
from python_generator import VAR, DEF, BLOCK, IMPORT, ARG, FOR, WHILE, CONTINUE, STR, BREAK, TUPLE, IF
from .. import Element, EOF


def META_BUILDER_1(name: str, fun: str, input_cls: Type[Element], output_cls: Type[Element]) -> DEF:
    """
    formal inputs : True
    formal outputs : True
    has_skips: False
    reflexive: False

    :param name: the wrapper name
    :param fun: the wrapped name
    :param input_cls: the input class of elements
    :param output_cls: the output class of elements
    :return:
    """
    SRC = VAR("src")
    CUR = VAR("cur")
    OLD = VAR("old")
    NEW = VAR("new")
    FUN = VAR(fun)
    CLS = VAR(output_cls.__name__)

    def CURSOR(i):
        return CLS.CALL(ARG("at", i), ARG("to", i), ARG("value", 0))

    GENERATOR = CUR.METH("develop", FUN.CALL(CUR, OLD), OLD)

    def UPDATE_CUR(obj):
        return CUR.ASSIGN(obj)

    NON_TERMINAL_CLAUSE = IF(NEW.GETATTR("is_terminal").NOT(), BLOCK(
        UPDATE_CUR(NEW),
        CONTINUE
    ))

    VALID_CLAUSE = IF(NEW.GETATTR("is_valid"), BLOCK(
        UPDATE_CUR(CURSOR(NEW.GETATTR("to"))),
        NEW.YIELD(),
        CONTINUE
    ))

    EOF_CLAUSE = IF(OLD.GETATTR("value").EQ(STR(EOF)), BLOCK(
        CLS.METH("EOF", OLD.GETATTR("to")).YIELD(),
        BREAK
    ))

    EACH_ITEM = BLOCK(
        WHILE(CUR.GETATTR("to").EQ(OLD.GETATTR("at")), BLOCK(
            NEW.ASSIGN(GENERATOR, t=output_cls),
            NON_TERMINAL_CLAUSE,
            VALID_CLAUSE,
            EOF_CLAUSE,
            IMPORT.FROM('item_engine', 'IE_SyntaxError'),
            VAR("IE_SyntaxError").CALL(CUR, OLD, NEW).RAISE()
        ))
    )

    return DEF(
        name=name,
        args=SRC.ARG(t=f"Iterator[{input_cls.__name__}]"),
        t=f"Iterator[{output_cls.__name__}]",
        block=BLOCK(
            # IMPORTS
            IMPORT.FROM("typing", "Iterator"),
            IMPORT.FROM(input_cls.__module__, input_cls.__name__),
            IMPORT.FROM(output_cls.__module__, output_cls.__name__),
            # INITS
            CUR.ASSIGN(CURSOR(0), t=output_cls),
            # START
            FOR(OLD, SRC, EACH_ITEM)
        )
    )
