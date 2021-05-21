from typing import Type
from python_generator import VAR, DEF, BLOCK, IMPORT, ARG, FOR, CONTINUE, STR, BREAK, IF, LIST, DICT, ITER_OVER, \
    COMPREHENSION
from .. import Element, EOF


def META_BUILDER_4(name: str, fun: str, input_cls: Type[Element], output_cls: Type[Element]) -> DEF:
    """
    formal inputs : True
    formal outputs : False
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

    CURS = VAR("curs")
    TO = VAR("to")
    RES = VAR("res")
    QUEUE = VAR("queue")
    I = VAR("i")

    def CURSOR(i):
        return CLS.CALL(ARG("at", i), ARG("to", i), ARG("value", 0))

    GENERATOR = COMPREHENSION(CUR.METH("develop", RES, OLD), RES, FUN.CALL(CUR, OLD)).GENE()

    ADD_CUR = DEF(
        "add_cur",
        CUR.ARG(t=output_cls),
        BLOCK(
            TO.ASSIGN(CUR.GETATTR("to")),
            IF(TO.NOT_IN(CURS), BLOCK(
                CURS.SETITEM(TO, LIST([CUR]))
            )).ELIF(CUR.NOT_IN(CURS.GETITEM(TO)), BLOCK(
                CURS.GETITEM(TO).METH("append", CUR)
            ))
        )
    )

    def UPDATE_CUR(obj):
        return ADD_CUR.CALL(obj)

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

    ITER_QUEUE = ITER_OVER(
        index=I,
        elements=QUEUE,
        element=CUR,
        element_type=output_cls,
        statements=[
            FOR(NEW, GENERATOR, BLOCK(
                NON_TERMINAL_CLAUSE,
                VALID_CLAUSE
            ))
        ]
    )

    EACH_ITEM = BLOCK(
        QUEUE.ASSIGN(CURS.METH("get", OLD.GETATTR("at"), LIST())),
        I.ASSIGN(0),
        ITER_QUEUE,
        EOF_CLAUSE
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
            IMPORT.FROM("typing", ["Dict", "List"]),
            # INITS
            CURS.ASSIGN(DICT(), t=f"Dict[int, List[{output_cls.__name__}]]"),
            ADD_CUR,
            ADD_CUR.CALL(CURSOR(0)),
            # START
            FOR(OLD, SRC, EACH_ITEM)
        )
    )
