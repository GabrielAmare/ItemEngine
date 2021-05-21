from typing import Type
from python_generator import VAR, DEF, BLOCK, IMPORT, ARG, FOR, CONTINUE, STR, BREAK, IF, LIST, DICT, ITER_OVER, \
    COMPREHENSION
from .. import Element


def META_BUILDER_5(name: str, fun: str, input_cls: Type[Element], output_cls: Type[Element]) -> DEF:
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
    STACK = VAR("stack")
    J = VAR("j")
    OBJ = VAR("obj")
    OLDR = VAR("oldr")

    def CURSOR(i):
        return CLS.CALL(ARG("at", i), ARG("to", i), ARG("value", 0))

    GENERATOR = COMPREHENSION(CUR.METH("develop", RES, OLDR), RES, FUN.CALL(CUR, OLDR)).GENE()

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

    # ADD_TO_STACK = DEF(
    #     "add_to_stack",
    #     OBJ.ARG(t=f"Union[{input_cls.__name__}, {output_cls.__name__}]"),
    #     IF(OBJ.NOT_IN(STACK), STACK.METH("insert", J, OBJ))
    # )

    def UPDATE_CUR(obj):
        return ADD_CUR.CALL(obj)

    NON_TERMINAL_CLAUSE = IF(NEW.GETATTR("is_terminal").NOT(), BLOCK(
        UPDATE_CUR(NEW),
        CONTINUE
    ))

    VALID_CLAUSE = IF(NEW.GETATTR("is_valid"), BLOCK(
        # ADD_TO_STACK.CALL(NEW),
        IF(NEW.NOT_IN(STACK), STACK.METH("insert", J, NEW)),
        UPDATE_CUR(CURSOR(NEW.GETATTR("to"))),
        NEW.YIELD(),
        CONTINUE
    ))

    EOF_CLAUSE = IF(OLD.GETATTR("value").EQ(STR("EOF")), BLOCK(
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
        QUEUE.ASSIGN(CURS.GETITEM(OLDR.GETATTR("at"))),
        UPDATE_CUR(CURSOR(OLDR.GETATTR("at"))),
        I.ASSIGN(0),
        ITER_QUEUE,
        CONTINUE
    )

    EACH_ITEM = BLOCK(
        STACK.METH("append", OLD),
        ITER_OVER(
            index=J,
            elements=STACK,
            element=OLDR,
            element_type=output_cls,
            statements=[
                IF(OLDR.GETATTR("at").IN(CURS), EACH_ITEM)
            ]
        ),
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
            IMPORT.FROM("typing", ["Union"]),
            # INITS
            CURS.ASSIGN(DICT(), t=f"Dict[int, List[{output_cls.__name__}]]"),
            ADD_CUR,
            ADD_CUR.CALL(CURSOR(0)),
            STACK.ASSIGN(LIST(), t=f"List[Union[{input_cls.__name__}, {output_cls.__name__}]]"),
            J.ASSIGN(0, t=int),
            # ADD_TO_STACK,
            # START
            FOR(OLD, SRC, EACH_ITEM)
        )
    )
