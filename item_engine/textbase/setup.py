"""
Builder for a package based on item_engine.textbase
"""

from python_generator import *


def setup(root: str, name: str):
    TEXT = VAR("text")
    LEMMA = VAR("lemma")
    PARSE = VAR("parse")

    package = PACKAGE(
        name,
        MODULE(
            "__init__",
            SCOPE(
                IMPORT.ALL(".make"),
                IMPORT.ALL(".main"),
                IMPORT.ALL(".test"),
            )
        ),
        MODULE(
            "make",
            SCOPE(
                IMPORT.ALL("item_engine.textbase"),
                VAR("__all__").ASSIGN(LIST([STR("engine")])),
                VAR("lexer").ASSIGN(VAR("MakeLexer").CALL(
                    VAR("keywords").ARG(LIST()),
                    VAR("symbols").ARG(LIST()),
                    VAR("branches").ARG(DICT()),
                )),
                VAR("parser").ASSIGN(VAR("MakeParser").CALL(
                    VAR("operators").ARG(DICT()),
                    VAR("branches").ARG(DICT()),
                )),
                VAR("engine").ASSIGN(VAR("Engine").CALL(
                    VAR("name").ARG(STR()),
                    VAR("parsers").ARG(LIST([
                        VAR("Parser").CALL(
                            VAR("name").ARG(STR("lexer")),
                            VAR("branch_set").ARG(VAR("lexer")),
                            VAR("input_cls").ARG(VAR("Char")),
                            VAR("output_cls").ARG(VAR("Token")),
                            VAR("formal_inputs").ARG(True),
                            VAR("formal_outputs").ARG(True),
                            VAR("reflexive").ARG(False),
                            VAR("skips").ARG(LIST())
                        ),
                        VAR("Parser").CALL(
                            VAR("name").ARG(STR("parser")),
                            VAR("branch_set").ARG(VAR("parser")),
                            VAR("input_cls").ARG(VAR("Char")),
                            VAR("output_cls").ARG(VAR("Token")),
                            VAR("formal_inputs").ARG(True),
                            VAR("formal_outputs").ARG(True),
                            VAR("reflexive").ARG(False),
                            VAR("skips").ARG(LIST())
                        )
                    ]))
                ))
            )
        ),
        MODULE(
            "main",
            SCOPE(
                IMPORT.FROM(f"{root}.{name}.engine", "parse"),
                IMPORT.FROM("item_engine.textbase", "make_characters"),
                DEF(
                    "get",
                    TEXT.ARG(t=str),
                    RETURN(
                        PARSE.CALL(
                            VAR("make_characters").CALL(
                                TEXT,
                                VAR("eof").ARG(True)
                            )
                        )
                    )
                ),
                DEF(
                    "main",
                    ARGS(),
                    WHILE(
                        True,
                        BLOCK(
                            TEXT.ASSIGN(VAR("input").CALL(STR("enter your text : "))),
                            IF(TEXT.NOT(), BREAK),
                            FOR(LEMMA, VAR("get").CALL(TEXT), VAR("print").CALL(LEMMA))
                        )
                    )
                )
            )
        ),
        MODULE(
            "test",
            SCOPE(
                IMPORT.FROM(f"{root}.{name}.make", "engine"),
                VAR("engine").METH("build", VAR("allow_overwrite").ARG(True))
            )
        )
    )

    package.save(allow_overwrite=False)
