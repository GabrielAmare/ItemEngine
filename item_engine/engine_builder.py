from __future__ import annotations

import os
from typing import List, Type, Union

from python_generator import *

from .build import OriginSelectData
from .elements import Element, IE_SyntaxError


class ParserConfig:
    def __init__(self, name: str,
                 input_cls: Type[Element],
                 output_cls: Type[Element],
                 strict_propagator: bool,
                 consecutive_outputs: bool,
                 recursive: bool,

                 skips: List[str] = None
                 ):
        self.name: str = name
        self.input_cls: Type[Element] = input_cls
        self.output_cls: Type[Element] = output_cls
        self.strict_propagator: bool = strict_propagator
        self.consecutive_outputs: bool = consecutive_outputs
        self.recursive: bool = recursive

        self.skips: List[str] = skips or []


class ParserBuild(ParserConfig):
    def _import(self, module: Union[str, type], *names: str) -> None:
        if isinstance(module, str):
            self.imports.append(IMPORT.FROM(module, list(names)))
        else:
            assert not names
            self.imports.append(IMPORT.TYPE(module))

    def _build_propagator_block(self, cur: VAR, old: VAR) -> BLOCK:
        raise NotImplementedError

    def _build_propagator_function(self) -> DEF:
        self._import(self.output_cls)
        cur = VAR("cur", t=self.output_cls)

        self._import(self.input_cls)
        old = VAR("old", t=self.input_cls)

        input_args = [cur.ARG(), old.ARG()]

        self._import("item_engine", "CASE")
        if self.strict_propagator:
            output_type = "CASE"
        else:
            self._import("typing", "Iterator")
            output_type = "Iterator[CASE]"

        return DEF(
            name=f"{self.name}_propagator",
            args=input_args,
            t=output_type,
            block=self._build_propagator_block(cur, old)
        )

    def _build_generator_function(self) -> DEF:
        self._import("typing", "Iterator")
        src = VAR("src", t=f"Iterator[{self.input_cls.__name__}]")
        input_args = [src.ARG()]
        output_type = f"Iterator[{self.output_cls.__name__}]"

        return DEF(
            name=self.name + '_generator',
            args=input_args,
            t=output_type,
            block=self._build_generator_block(src)
        )

    def _build_generator_block(self, src: VAR) -> BLOCK:
        raise NotImplementedError

    def _build_other_functions(self) -> List[DEF]:
        raise NotImplementedError

    def _build_main_function(self) -> DEF:
        self._import("typing", "Iterator")
        src = VAR("src", t=f"Iterator[{self.input_cls.__name__}]")
        input_args = [src.ARG()]
        output_type = f"Iterator[{self.output_cls.__name__}]"

        result = self.generator.CALL(src)

        for function in self.functions:
            result = function.CALL(result)

        return DEF(
            name=f"{self.name}",
            args=input_args,
            t=output_type,
            block=[
                RETURN(result)
            ]
        )

    def _build_module(self) -> MODULE:
        return MODULE(name=self.name, scope=[
            *self.imports,
            VAR("__all__").ASSIGN(LIST([STR(self.main_function.name.name)])),
            self.propagator,
            self.generator,
            *self.functions,
            self.main_function
        ])

    def __init__(self, **config):
        super().__init__(**config)

        self.imports: List[IMPORT.FROM] = []

        self.propagator: DEF = self._build_propagator_function()
        self.functions: List[DEF] = self._build_other_functions()
        self.generator: DEF = self._build_generator_function()
        self.main_function: DEF = self._build_main_function()

        self.module: MODULE = self._build_module()

    def import_main_function(self, root: str) -> IMPORT.FROM:
        return IMPORT.FROM(f"{root}{self.name}", f"{self.main_function.name!s}")

    def save(self, root=os.curdir, allow_overwrite: bool = False):
        self.module.save(root, allow_overwrite)


class ParserBuildOSD(ParserBuild):
    def __init__(self, osd: OriginSelectData, **config):
        self.osd: OriginSelectData = osd

        super().__init__(**config)

    def _build_propagator_block(self, cur: VAR, old: VAR) -> BLOCK:
        return self.osd.code(cur, old, self.strict_propagator)

    def _build_generator_block(self, src: VAR) -> BLOCK:
        raise NotImplementedError

    def _build_other_functions(self) -> List[DEF]:
        functions: List[DEF] = []

        if self.skips:
            functions.append(self._build_skip_function())

            if self.consecutive_outputs:
                functions.append(self._build_reassign_function())

        return functions

    def _build_skip_function(self) -> DEF:
        """
        def tokenizer_skips(src: Iterator[Token]) -> Iterator[Token]:
            for old in src:
                if old.value == 'WHITESPACE':
                    continue
                yield old
        """
        assert self.skips
        self._import("typing", "Iterator")
        src = VAR("src", t=f"Iterator[{self.output_cls.__name__}]")
        input_args = [src.ARG()]
        output_type = f"Iterator[{self.output_cls.__name__}]"

        inp = VAR("inp", t=self.output_cls)

        if len(self.skips) == 1:
            condition = inp.GETATTR("value").EQ(STR(self.skips[0]))
        else:
            condition = inp.GETATTR("value").IN(LIST(list(map(STR, self.skips))))

        return DEF(
            name=self.name + '_skips',
            args=input_args,
            t=output_type,
            block=[
                FOR(inp, src, [
                    IF(condition, CONTINUE),
                    YIELD(inp)
                ])
            ]
        )

    def _build_reassign_function(self) -> DEF:
        """
        def tokenizer_reassign(src: Iterator[Token]) -> Iterator[Token]:
            for pos, old in enumerate(src):
                yield old.replace(at=pos, to=pos + 1)
        """
        self._import("typing", "Iterator")
        src = VAR("src", t=f"Iterator[{self.output_cls.__name__}]")
        input_args = [src.ARG()]
        output_type = f"Iterator[{self.output_cls.__name__}]"

        inp = VAR("inp", t=self.output_cls)
        pos = VAR("pos", t=int)

        return DEF(
            name=self.name + '_reassign',
            args=input_args,
            t=output_type,
            block=[
                FOR(ARGS(pos, inp), VAR("enumerate").CALL(src), [
                    IF(inp.GETATTR("to").GT(inp.GETATTR("at")), [
                        YIELD(inp.METH("replace", VAR("at").ARG(pos), VAR("to").ARG(ADD(pos, INT(1)))))
                    ], ELSE(
                        YIELD(inp.METH("replace", VAR("at").ARG(pos), VAR("to").ARG(pos)))
                    ))
                ])
            ]
        )


class ParserBuildGenerators(ParserBuildOSD):
    @staticmethod
    def _element_handling(new: VAR, NT: List[STATEMENT], TV: List[STATEMENT], TE: List[STATEMENT] = None) -> IF:
        return IF(
            NOT(ISINSTANCE(new.GETATTR("value"), VAR("str"))),
            NT,
            ELIF(
                NOT(new.GETATTR("value").METH("startswith", STR("!"))),
                TV,
                ELSE(
                    *TE
                )
            )
        )

    def _build_generator_block(self, src: VAR) -> BLOCK:
        if self.strict_propagator and not self.recursive:
            return self._build_generator_1(src)

        if not self.strict_propagator and self.recursive:
            return self._build_generator_2(src)

        return BLOCK(
            COMMENT("the code generator was unable to find the required code for this configuration :"),
            COMMENT(f"--> ``strict_propagator={self.strict_propagator}``"),
            COMMENT(f"--> ``recursive={self.recursive}``"),
            COMMENT(""),
            COMMENT(f"Valid configurations are: for params (strict_propagator, recursive)"),
            COMMENT(f"  - (True, False)"),
            COMMENT(f"  - (False, True)"),
            COMMENT(""),
            COMMENT(f"Current configuration :"),
            COMMENT(f"  > ({self.strict_propagator}, {self.recursive})"),
            RAISE(VAR("NotImplementedError"))
        )

    def _build_generator_1(self, src: VAR) -> BLOCK:
        """
        def tokenizer_generator(src: Iterator[Char]) -> Iterator[Token]:
            cur: Token = Token.cursor(0)
            for old in src:
                while cur.to == old.at:
                    new: Token = cur.develop(tokenizer_propagator(cur, old), old)
                    if isinstance(new.value, str):
                        if new.value.startswith('!'):
                            if old.value == 'EOF':
                                break
                            else:
                                raise IE_SyntaxError(new)
                        else:
                            yield new
                            cur: Token = Token.cursor(new.to)
                    elif new.to == old.to:
                        cur: Token = new
                    else:
                        raise IE_SyntaxError(new)

            yield cur.eof()
        """
        assert self.strict_propagator
        assert not self.recursive

        old = VAR("old", t=self.input_cls)
        cur = VAR("cur", t=self.output_cls)
        new = VAR("new", t=self.output_cls)

        output_cls = VAR(self.output_cls.__name__)

        # safe = False
        # if safe:
        #     ERROR = BREAK
        # else:
        self._import(IE_SyntaxError)
        ERROR = RAISE(VAR("IE_SyntaxError").CALL(new))

        return BLOCK(
            cur.ASSIGN(output_cls.METH("cursor", INT(0))),
            FOR(old, src, [
                WHILE(cur.GETATTR("to").EQ(old.GETATTR("at")), [
                    new.ASSIGN(cur.METH("develop", self.propagator.CALL(cur, old), old)),
                    self._element_handling(new, NT=[
                        IF(EQ(new.GETATTR("to"), old.GETATTR("to")), [
                            cur.ASSIGN(new),
                        ], ELSE(
                            ERROR
                        ))
                    ], TV=[
                        YIELD(new),
                        cur.ASSIGN(output_cls.METH("cursor", new.GETATTR("to"))),
                        CONTINUE
                    ], TE=[
                        IF(old.GETATTR("value").EQ(STR("EOF")), [
                            BREAK
                        ], ELSE(
                            ERROR
                        ))
                    ])
                    # IF(ISINSTANCE(new.GETATTR("value"), VAR("str")), [
                    #     IF(new.GETATTR("value").METH("startswith", STR("!")), [
                    #         IF(old.GETATTR("value").EQ(STR("EOF")), [
                    #             BREAK
                    #         ], ELSE(
                    #             ERROR
                    #         ))
                    #     ]),
                    #     YIELD(new),
                    #     cur.ASSIGN(output_cls.METH("cursor", new.GETATTR("to"))),
                    #     CONTINUE
                    # ], ELIF(EQ(new.GETATTR("to"), old.GETATTR("to")), [
                    #     cur.ASSIGN(new),
                    # ], ELSE(
                    #     ERROR
                    # )))
                ])
            ]),
            YIELD(cur.METH("eof"))
        )

    def _build_generator_2(self, src: VAR) -> BLOCK:
        """
        # --recursive = True
        # --consecutive-inputs = True
        # --strict-propagator = False  # only one new element can be generated from a (cur, old) pair

        def lemmatizer_generator(src: Iterator[Token]) -> Iterator[Lemma]:
            eof: int = 0
            queue: Deque[Union[Token, Lemma]] = deque()
            non_terminals: Dict[int, List[Lemma]] = {}
            terminals: List[Lemma] = []
            outputs: List[Lemma] = []
            new_ends: Set[int] = set()

            def add_terminal(e):
                if e not in terminals:
                    terminals.append(e)
                    queue.append(e)
                    new_ends.add(e.to)
                    outputs.append(e)

            def add_non_terminal(e):
                if e.to not in non_terminals:
                    non_terminals[e.to] = [e]
                    new_ends.add(e.to)
                elif e not in non_terminals[e.to]:
                    non_terminals[e.to].append(e)
                    new_ends.add(e.to)

            def add_cursor(at):
                cursor = Lemma.cursor(at)
                add_non_terminal(cursor)

            def get_non_terminals(at):
                if at in non_terminals:
                    yield from non_terminals[at]

            add_cursor(0)

            for inp in src:
                eof = inp.to
                queue.append(inp)

                while queue:
                    old = queue.popleft()

                    for cur in get_non_terminals(old.at):
                        for case in lemmatizer_propagator(cur, old):
                            new = cur.develop(case, old)

                            if not isinstance(new.value, str):
                                # NON-TERMINAL
                                add_non_terminal(new)
                                continue
                            elif not new.value.startswith('!'):
                                # TERMINAL-VALID
                                add_terminal(new)
                                continue
                            else:
                                # TERMINAL-ERROR
                                continue

                    for to in new_ends:
                        add_cursor(to)
                    new_ends = set()

                    if inp.value == 'EOF':
                        if outputs:
                            queue.append(inp)

                    for output in sorted(outputs, key=lambda out: (out.to, out.at)):
                        yield output
                    outputs = []


            yield Lemma.EOF(at=eof)
        """
        assert not self.strict_propagator
        assert self.recursive

        self._import("typing", "Deque", "Union", "Dict", "List", "Set", "Iterator")
        self._import("collections", "deque")
        self._import(self.input_cls)
        self._import(self.output_cls)

        # VARS DEFINITION
        eof = VAR("eof", t=int)
        queue = VAR("queue", t=f"Deque[Union[{self.input_cls.__name__}, {self.output_cls.__name__}]]")
        non_terminals = VAR("non_terminals", t=f"Dict[int, List[{self.output_cls.__name__}]]")
        terminals = VAR("terminals", t=f"List[{self.output_cls.__name__}]")
        outputs = VAR("outputs", t=f"List[{self.output_cls.__name__}]")
        new_ends = VAR("new_ends", t="Set[int]")

        e = VAR("e", t=self.output_cls)
        at = VAR("at", t=int)
        output_class = VAR(self.output_cls.__name__)

        # VARS INITIAL VALUE
        VAR_INITS = [
            eof.ASSIGN(INT(0)),
            queue.ASSIGN(VAR("deque").CALL()),
            non_terminals.ASSIGN(DICT()),
            terminals.ASSIGN(LIST()),
            outputs.ASSIGN(LIST()),
            new_ends.ASSIGN(VAR("set").CALL())
        ]

        add_terminal = DEF(name="add_terminal", args=e.ARG(), block=[
            IF(NOT_IN(e, terminals), [
                terminals.METH("append", e),
                queue.METH("append", e),
                outputs.METH("append", e),
                new_ends.METH("add", e.GETATTR("to")),
            ])
        ])

        add_non_terminal = DEF(name="add_non_terminal", args=e.ARG(), block=[
            IF(e.GETATTR("to").NOT_IN(non_terminals), [
                non_terminals.SETITEM(e.GETATTR("to"), LIST([e])),
                new_ends.METH("add", e.GETATTR("to")),
            ], ELIF(e.NOT_IN(non_terminals.GETITEM(e.GETATTR("to"))), [
                non_terminals.GETITEM(e.GETATTR("to")).METH("append", e),
                new_ends.METH("add", e.GETATTR("to"))
            ]))
        ])

        add_cursor = DEF(name="add_cursor", args=at.ARG(), block=[
            add_non_terminal.CALL(output_class.METH("cursor", at))
        ])

        get_non_terminals = DEF(name="get_non_terminals", args=at.ARG(), block=[
            IF(at.IN(non_terminals), [
                YIELD.FROM(non_terminals.GETITEM(at))
            ])
        ])

        FUNCTIONS = [
            add_terminal,
            add_non_terminal,
            add_cursor,
            get_non_terminals
        ]

        old = VAR("old", t=f"Union[{self.input_cls.__name__}, {self.output_cls.__name__}]")
        inp = VAR("inp", t=self.input_cls)
        cur = VAR("cur", t=self.output_cls)
        new = VAR("new", t=self.output_cls)
        case = VAR("case")
        to = VAR("to", t=int)
        output = VAR("output", t=self.output_cls)

        out = VAR("out")
        sort_outputs = LAMBDA(ARGS(out), TUPLE((out.GETATTR("to"), out.GETATTR("at"))))

        return BLOCK(
            *VAR_INITS,
            *FUNCTIONS,
            add_cursor.CALL(INT(0)),
            FOR(inp, src, [
                eof.ASSIGN(inp.GETATTR("to")),
                queue.METH("append", inp),

                WHILE(queue, [
                    old.ASSIGN(queue.METH("popleft")),
                    FOR(cur, get_non_terminals.CALL(old.GETATTR("at")), [
                        FOR(case, self.propagator.CALL(cur, old), [
                            new.ASSIGN(cur.METH("develop", case, old)),
                            self._element_handling(new, NT=[
                                add_non_terminal.CALL(new),
                                CONTINUE
                            ], TV=[
                                add_terminal.CALL(new),
                                CONTINUE
                            ], TE=[
                                CONTINUE
                            ])
                        ])
                    ]),
                    FOR(to, new_ends, [
                        add_cursor.CALL(to),
                    ]),
                    new_ends.ASSIGN(VAR("set").CALL()),
                    IF(inp.GETATTR("value").EQ(STR("EOF")), [
                        IF(outputs, [
                            queue.METH("append", inp)
                        ])
                    ]),
                    FOR(output, VAR("sorted").CALL(outputs, VAR("key").ARG(v=sort_outputs)), [
                        YIELD(output)
                    ]),
                    outputs.ASSIGN(LIST())
                ])
            ]),
            YIELD(output_class.METH("EOF", VAR("at").ARG(eof)))
        )


class EngineConfig:
    def __init__(self,
                 package_name: str,
                 wrapper_name: str,
                 input_cls: Type[Element],
                 output_cls: Type[Element],

                 text_input: bool = False,
                 strict_output: bool = False
                 ):
        self.package_name: str = package_name
        self.wrapper_name: str = wrapper_name
        self.input_cls: Type[Element] = input_cls
        self.output_cls: Type[Element] = output_cls

        self.text_input: bool = text_input
        self.strict_output: bool = strict_output


class EngineBuild(EngineConfig):
    def _import(self, module: Union[str, type], *names: str) -> None:
        if isinstance(module, str):
            self.imports.append(IMPORT.FROM(module, list(names)))
        else:
            assert not names
            self.imports.append(IMPORT.TYPE(module))

    def _build_pre_functions(self) -> List[DEF]:
        raise NotImplementedError

    def _build_post_functions(self) -> List[DEF]:
        raise NotImplementedError

    def _build_main_function(self) -> DEF:

        if self.text_input:
            input_type = str
        else:
            self._import("typing", "Iterator")
            self._import(self.input_cls)
            input_type = f"Iterator[{self.input_cls.__name__}]"

        if self.strict_output:
            output_type = self.output_cls.__name__
        else:
            self._import("typing", "Iterator")
            self._import(self.output_cls)
            output_type = f"Iterator[{self.output_cls.__name__}]"

        src = VAR("src", t=input_type)

        res = src

        for function in self.pre_functions:
            res = function.CALL(res)

        for parser in self.parsers:
            self.imports.append(parser.import_main_function(root='.'))
            res = parser.main_function.CALL(res)

        for function in self.post_functions:
            res = function.CALL(res)

        return DEF(
            name=self.wrapper_name,
            args=src.ARG(),
            t=output_type,
            block=RETURN(res)
        )

    def _build_modules(self, custom_modules: List[MODULE]) -> List[MODULE]:
        for module in custom_modules:
            self._import(f'.{module.name!s}', '*')

        return [parser.module for parser in self.parsers] + custom_modules

    def _build_module(self) -> MODULE:
        return MODULE(name='__init__', scope=[
            *self.imports,
            # VAR("__all__").ASSIGN(LIST([STR(f"{self.main_function.name!s}")])),
            *self.pre_functions,
            *self.post_functions,
            self.main_function
        ])

    def _build_package(self) -> PACKAGE:
        return PACKAGE(self.package_name, *[
            self.module,
            *self.modules
        ])

    def __init__(self, parsers: List[ParserBuild], custom_modules: List[MODULE] = None, **config):
        super().__init__(**config)
        self.parsers: List[ParserBuild] = parsers

        self.imports: List[IMPORT.FROM] = []

        self.modules: List[MODULE] = self._build_modules(custom_modules or [])
        self.pre_functions: List[DEF] = self._build_pre_functions()
        self.post_functions: List[DEF] = self._build_post_functions()
        self.main_function: DEF = self._build_main_function()
        self.module: MODULE = self._build_module()
        self.package: PACKAGE = self._build_package()


class EngineBuildProcessFunctions(EngineBuild):
    def _build_pre_functions(self) -> List[DEF]:
        functions: List[DEF] = []

        if self.text_input:
            functions.append(self._build_characters_function())

        return functions

    def _build_post_functions(self) -> List[DEF]:
        functions: List[DEF] = []

        if self.strict_output:
            functions.append(self._build_toplevel_function())

        return functions

    def _build_characters_function(self) -> DEF:
        """
            def characters(src: str) -> Iterator[Char]:
                i = -1
                for i, char in enumerate(src):
                    yield Char(at=i, to=i + 1, value=char)
                yield Char.EOF(i + 1)
        """
        self._import("typing", "Iterator")
        self._import("item_engine.textbase", "Char")
        src = VAR("src", t=str)
        input_args = [src.ARG()]
        output_type = f"Iterator[Char]"

        output_cls = VAR("Char")
        pos = VAR("pos", t=int)
        inp = VAR("char", t=str)

        return DEF(name=self.wrapper_name + "_characters", args=input_args, t=output_type, block=[
            pos.ASSIGN(INT(-1)),
            FOR(ARGS(pos, inp), VAR("enumerate").CALL(src), [
                YIELD(output_cls.CALL(
                    VAR("at").ARG(pos),
                    VAR("to").ARG(ADD(pos, INT(1))),
                    VAR("value").ARG(inp)
                ))
            ]),
            YIELD(output_cls.METH("EOF", ADD(pos, INT(1))))
        ])

    def _build_toplevel_function(self) -> DEF:
        """
            def keep_toplevel(src: Iterator[Lemma]) -> Lemma:
                res = []
                to = 0
                for inp in src:
                    if inp.at == 0:
                        if inp.to > to:
                            to = inp.to
                            res = [inp]
                        elif inp.to == to:
                            res.append(inp)

                if len(res) == 1:
                    return res[0]
                elif res:
                    raise Exception('multiple wrapper elements found')
                else:
                    raise Exception('no wrapper element found')
        """
        self._import("typing", "Iterator")
        self._import(self.output_cls)

        src = VAR("src", t=f"Iterator[{self.output_cls.__name__}]")
        input_args = [src.ARG()]
        output_type = self.output_cls

        self._import("typing", "List")
        res = VAR("res", t=f"List[{self.output_cls.__name__}]")
        to = VAR("to", t=int)
        eof = VAR("eof", t=int)
        inp = VAR("inp", t=self.output_cls)
        out = VAR("out", t=self.output_cls)

        return DEF(name=self.wrapper_name + '_toplevel', args=input_args, t=output_type, block=[
            res.ASSIGN(LIST()),
            to.ASSIGN(INT(0)),
            eof.ASSIGN(INT(0)),
            FOR(inp, src, [
                IF(inp.GETATTR("value").EQ(STR("EOF")), [
                    eof.ASSIGN(inp.GETATTR("at")),
                    BREAK
                ]),
                IF(inp.GETATTR("at").EQ(INT(0)), [
                    IF(inp.GETATTR("to").GT(to), [
                        to.ASSIGN(inp.GETATTR("to")),
                        res.ASSIGN(LIST([inp]))
                    ], ELIF(inp.GETATTR("to").EQ(to), [
                        res.METH("append", inp)
                    ]))
                ])
            ]),
            IF(VAR("len").CALL(res).EQ(INT(1)), [
                out.ASSIGN(res.GETITEM(INT(0))),
                IF(out.GETATTR("to").EQ(eof), [
                    RETURN(out)
                ], ELSE(
                    RAISE(EXCEPTION(STR('no complete wrapper element found')))
                ))
            ], ELIF(res, [
                RAISE(EXCEPTION(STR('multiple wrapper elements found')))
            ], ELSE(
                RAISE(EXCEPTION(STR('no wrapper element found')))
            )))
        ])
