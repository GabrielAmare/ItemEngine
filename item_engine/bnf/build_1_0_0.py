from __future__ import annotations

from functools import reduce
from typing import List, Dict, Union, Tuple, Iterator

from python_generator import *

from item_engine.build import Optimizer
from item_engine.constants import INF, INCLUDE, INCLUDE_AS, INCLUDE_IN as IN_
from item_engine.engine_builder import ParserBuildGenerators, EngineBuildProcessFunctions
from item_engine.rules import Branch, BranchSet, Rule, All as All_rule, Match as Match_rule, VALID
from item_engine.textbase.functions import string, charset
from item_engine.textbase.items import Char, Token, Lemma, CharG, TokenG, TokenI

import item_engine.bnf.grammar as gr


class ClassBuild:
    def __init__(self, name: str):
        self.name: str = name
        self.order: int = 0
        self.direct_sups: List[ClassBuild] = []
        self.direct_subs: List[ClassBuild] = []

    def all_subs(self) -> Iterator[ClassBuild]:
        if self.direct_subs:
            for cls in self.direct_subs:
                yield from cls.all_subs()
        else:
            yield self

    def add_sup(self, sup: ClassBuild):
        assert sup not in self.direct_sups, 'duplicate'
        assert sup not in self.all_subs(), 'tautology'
        self.direct_sups.append(sup)
        sup.direct_subs.append(self)
        sup.order = max(sup.order, self.order + 1)

    def get_herits(self) -> List[str]:
        return [sup.name for sup in self.direct_sups]


class OperatorBuild(ClassBuild):
    def __init__(self, context: EngineBuilder, operator: gr.Operator):
        super().__init__(name=operator.name)

        self.context: EngineBuilder = context
        self.operator: gr.Operator = operator

        self.init_vars = self.context.get_init_vars(self.operator.rule)
        self.sign = self.context.get_sign(self.operator.rule)

    def _get_init_meth(self) -> DEF:
        return DEF(
            name='__init__',
            args=ARGS(SELF, *[var.ARG() for var in self.init_vars]),
            block=[
                SELF.SETATTR(var.name, var, t=var.t) for var in self.init_vars
            ]
        )

    def _get_str_block(self) -> BLOCK:
        return BLOCK(RETURN(self.context.get_str_of(self.operator.rule)))

    def _get_repr_block(self) -> BLOCK:
        repr_args = ", ".join(f"{{self.{var.name}!r}}" for var in self.init_vars)
        return BLOCK(RETURN(FSTR("{self.__class__.__name__}(" + repr_args + ")")))

    def _get_eq_block(self) -> BLOCK:
        eq_args = [SELF.GETATTR(var.name).EQ(VAR("other").GETATTR(var.name)) for var in self.init_vars]
        return BLOCK(IF(
            VAR("type").CALL(SELF).IS(VAR("type").CALL(VAR("other"))),
            BLOCK(
                RETURN(reduce(AND, eq_args))
            ), ELSE(
                RETURN(VAR("NotImplemented"))
            )
        ))

    def get_class(self) -> CLASS:
        return CLASS(
            name=self.operator.name,
            herits=sorted(self.get_herits()) or None,
            block=[
                self._get_init_meth(),
                DEF(name='__str__', args=ARGS(SELF), block=self._get_str_block()),
                DEF(name='__repr__', args=ARGS(SELF), block=self._get_repr_block()),
                DEF(name='__eq__', args=ARGS(SELF, VAR("other")), block=self._get_eq_block()),
                VAR("__hash__").ASSIGN(NONE)
            ]
        )

    def get_builder(self, builder: OBJECT, obj: VAR) -> BLOCK:
        cls = VAR(self.operator.name)

        args = []

        for match in self.sign:
            param = VAR(match.key)
            value = obj.GETATTR("data").GETITEM(STR(match.key))
            if isinstance(match, gr.MatchAs):
                # if match.name in self.context.builds:
                value = builder.CALL(value)
            elif isinstance(match, gr.MatchIn):
                # if match.name in self.context.builds:
                value = VAR("list").CALL(VAR("map").CALL(builder, value))
            else:
                raise TypeError(type(match))
            args.append(param.ARG(value))

        return BLOCK(RETURN(cls.CALL(*args)))


class GroupBuild(ClassBuild):
    def __init__(self, context: EngineBuilder, group: gr.Group):
        super().__init__(name=group.name)
        self.context: EngineBuilder = context
        self.group: gr.Group = group

    def get_class(self) -> CLASS:
        return CLASS(
            name=self.group.name,
            herits=sorted(self.get_herits()) or None,
            block=[

            ]
        )


class EngineBuilder:
    def __init__(self,
                 engine_name: str,
                 whitespace: str = ' ',
                 symbol_table: Dict[str, str] = None,
                 type_aliases: Dict[str, type] = None,
                 skips: List[str] = None):
        self.engine_name: str = engine_name

        self.whitespace: str = ''.join(sorted(set(whitespace)))
        self.symbol_table: Dict[str, str] = symbol_table or {}
        self.type_aliases: Dict[str, type] = type_aliases or {}
        self.skips: List[str] = skips or []

        self.__imports__: List[IMPORT.FROM] = []

        self.builds: Dict[str, Union[OperatorBuild, GroupBuild]] = {}

    def _get_literal_expr(self, literal: gr.Str) -> str:
        expr = eval(literal.content).strip(self.whitespace)
        if expr:
            return expr
        else:
            raise ValueError(literal)

    def _get_literal_name(self, literal: gr.Str) -> str:
        name = self._get_literal_expr(literal)
        for key, val in self.symbol_table.items():
            name = name.replace(key, val)
        return name

    def get_sign(self, obj) -> List[Union[gr.MatchAs, gr.MatchIn]]:
        if isinstance(obj, gr.Str):
            return []
        elif isinstance(obj, gr.Match):
            return []
        elif isinstance(obj, gr.MatchAs):
            return [obj]
        elif isinstance(obj, gr.MatchIn):
            return [obj]
        elif isinstance(obj, gr.All):
            res = []
            for child in obj.args:
                for var in self.get_sign(child):
                    if var in res:
                        raise Exception("variable name duplication in All is not allowed !")
                    res.append(var)
            return res
        elif isinstance(obj, gr.Any):
            first, *args = obj.args
            res = self.get_sign(first)
            for arg in args:
                if res != self.get_init_vars(arg):
                    raise Exception("different variables signature in Any is not allowed")
            return res
        elif isinstance(obj, gr.Enum):
            return self.get_sign(obj.child)
        else:
            raise TypeError(type(obj))

    def get_init_vars(self, obj) -> List[VAR]:
        if isinstance(obj, gr.Str):
            return []
        elif isinstance(obj, gr.Match):
            return []
        elif isinstance(obj, gr.MatchAs):
            return [VAR(
                name=obj.key,
                t=self._get_type(obj.name)
            )]
        elif isinstance(obj, gr.MatchIn):
            self.__imports__.append(IMPORT.FROM("typing", "List"))
            return [VAR(
                name=obj.key,
                t=f"List[{self._get_type(obj.name, force_string=True)}]"
            )]
        elif isinstance(obj, gr.All):
            res = []
            for child in obj.args:
                for var in self.get_init_vars(child):
                    if var in res:
                        raise Exception("variable name duplication in All is not allowed !")
                    res.append(var)
            return res
        elif isinstance(obj, gr.Any):
            first, *args = obj.args
            res = self.get_init_vars(first)
            for arg in args:
                if res != self.get_init_vars(arg):
                    raise Exception("different variables signature in Any is not allowed")
            return res
        elif isinstance(obj, gr.Optional):
            raise NotImplementedError
        elif isinstance(obj, gr.Repeat):
            raise NotImplementedError
        elif isinstance(obj, gr.Enum):
            return self.get_init_vars(obj.child)
        elif isinstance(obj, gr.Grammar):
            raise NotImplementedError
        else:
            raise TypeError(type(obj))

    def get_str_of(self, obj: Union[gr.Any_, gr.Operator, gr.Group, gr.Grammar]) -> EXPRESSION:
        if isinstance(obj, gr.Str):
            return STR(eval(obj.content))
        elif isinstance(obj, gr.MatchAs):
            return VAR("str").CALL(SELF.GETATTR(obj.key))
        elif isinstance(obj, gr.MatchIn):
            return VAR("map").CALL(VAR("str"), SELF.GETATTR(obj.key))
        elif isinstance(obj, gr.All):
            arg, *args = map(self.get_str_of, obj.args)
            for new in args:
                arg = ADD(arg, new)
            return arg
        elif isinstance(obj, gr.Enum):
            sep = self.get_str_of(obj.separator)
            if isinstance(sep, OBJECT):
                return sep.METH("join", self.get_str_of(obj.child))
            else:
                raise NotImplementedError
        else:
            raise TypeError(type(obj))

    def _register_class(self, obj: gr.GrammarRule) -> None:
        if isinstance(obj, gr.Operator):
            self.builds[obj.name] = OperatorBuild(context=self, operator=obj)
        elif isinstance(obj, gr.Group):
            self.builds[obj.name] = GroupBuild(context=self, group=obj)
            self.type_aliases[obj.name] = obj.names
        else:
            raise TypeError(type(obj))

    def _get_type(self, name: str, force_string: bool = False) -> Union[str, type]:
        if name in self.type_aliases:
            type_ = self.type_aliases[name]
            if force_string:
                return type_.__name__

            return type_

        return name

    def _import_from(self, module, thing):
        self.__imports__.append(IMPORT.FROM(module, thing))

    def _list_all(self, grammar: gr.Grammar) -> Tuple[List[gr.Group], List[gr.Operator]]:
        groups = []
        operators = []
        for branch in grammar.branches:
            self._register_class(branch)
            if isinstance(branch, gr.Group):
                groups.append(branch)
            elif isinstance(branch, gr.Operator):
                operators.append(branch)
            else:
                raise TypeError(type(branch))

        for group in groups:
            for name in group.names:
                if name in self.builds:
                    self.builds[name].add_sup(self.builds[group.name])
                else:
                    raise Exception(f"cannot add a super to undefined class {name!r} !")

        return groups, operators

    def _get_tokenizer_branches(self, obj) -> Iterator[Branch]:
        if isinstance(obj, gr.Operator):
            yield from self._get_tokenizer_branches(obj.rule)
        elif isinstance(obj, (gr.All, gr.Any)):
            for arg in obj.args:
                yield from self._get_tokenizer_branches(arg)
        elif isinstance(obj, gr.Str):
            try:
                expr = self._get_literal_expr(obj)
                name = self._get_literal_name(obj)
                yield Branch(
                    name=name,
                    rule=string(expr),
                    priority=100 + len(expr)
                )
            except ValueError:
                pass
        elif isinstance(obj, gr.Enum):
            yield from self._get_tokenizer_branches(obj.separator)

    def _get_tokenizer_branchset(self,
                                 operators: List[gr.Operator],
                                 patterns: List[Branch]
                                 ) -> Union[BranchSet, Branch]:
        branches = [
            Branch(
                name="WHITESPACE",
                rule=charset(self.whitespace).inc().repeat(1, INF),
                priority=0
            ),
            *patterns
        ]
        for operator in operators:
            branches.extend(self._get_tokenizer_branches(operator))

        return BranchSet.make(*branches) if branches else None

    def _get_token_group(self, name: str) -> TokenG:
        """Return the token group associated with a name"""
        if name in self.builds:
            names = [sub.name for sub in self.builds[name].all_subs()]
        else:
            names = [name]
        return TokenG(map(TokenI, names)) / TokenG({TokenI(name='EOF')})

    def _get_lemmatizer_rule(self, obj) -> Rule:
        if isinstance(obj, gr.Group):
            raise NotImplementedError
        elif isinstance(obj, gr.All):
            return All_rule.join(map(self._get_lemmatizer_rule, obj.args))
        elif isinstance(obj, gr.Str):
            try:
                name = self._get_literal_name(obj)
                return Match_rule(
                    group=TokenG({TokenI(name=name)}) / TokenG({TokenI(name='EOF')}),
                    action=INCLUDE
                )
            except ValueError:
                return VALID
        elif isinstance(obj, gr.Match):
            return Match_rule(
                group=self._get_token_group(obj.name),
                action=INCLUDE
            )
        elif isinstance(obj, gr.MatchAs):
            return Match_rule(
                group=self._get_token_group(obj.name),
                action=INCLUDE_AS.format(obj.key)
            )
        elif isinstance(obj, gr.MatchIn):
            return Match_rule(
                group=self._get_token_group(obj.name),
                action=IN_.format(obj.key)
            )
        elif isinstance(obj, gr.Enum):
            MN = 1
            child = self._get_lemmatizer_rule(obj.child)
            try:
                separator = self._get_lemmatizer_rule(obj.separator)
                return child & (separator & child).repeat(MN, INF)
            except ValueError:
                return child.repeat(MN + 1, INF)
        else:
            raise TypeError(type(obj))

    def _get_lemmatizer_branchset(self, operators: List[gr.Operator]) -> Union[BranchSet, Branch]:
        branches = []
        for operator in operators:
            branches.append(
                Branch(
                    name=operator.name,
                    rule=self._get_lemmatizer_rule(operator.rule),
                    priority=0
                )
            )

        return BranchSet.make(*branches) if branches else None

    def _generate_build_function(self) -> DEF:
        obj = VAR("obj")
        input_args = [obj.ARG()]

        operator_builds = [
            build
            for build in sorted(self.builds.values(), key=lambda build: -build.order)
            if isinstance(build, OperatorBuild)
        ]
        obj = VAR("obj")
        builder = VAR("build")

        self.__imports__.append(IMPORT.TYPE(Token))
        self.__imports__.append(IMPORT.TYPE(Lemma))

        switch = SWITCH(cases=[
            (
                ISINSTANCE(obj, VAR("Lemma")),
                SWITCH(cases=[
                    (obj.GETATTR("value").EQ(STR(build.name)), build.get_builder(builder, obj))
                    for build in operator_builds
                ], default=RAISE(VAR("ValueError").CALL(obj.GETATTR("value"))))
            ), (
                ISINSTANCE(obj, VAR("Token")),
                RETURN(obj.GETATTR("content"))
            )
        ], default=RAISE(VAR("TypeError").CALL(VAR("type").CALL(obj))))

        return DEF(name='build', args=input_args, block=switch)

    def generate_engine(self, grammar: gr.Grammar, patterns: List[Branch] = None,
                        safe: bool = False) -> EngineBuildProcessFunctions:
        self._import_from("__future__", "annotations")

        groups, operators = self._list_all(grammar)

        tokenizer = ParserBuildGenerators(
            name='tokenizer',
            input_cls=Char,
            output_cls=Token,

            skips=["WHITESPACE"] + self.skips,
            consecutive_outputs=True,

            strict_propagator=True,
            recursive=False,

            osd=Optimizer(
                branch_set=self._get_tokenizer_branchset(operators, patterns or []),
                group_cls=CharG
            ).data(strict_propagator=True)

        )
        lemmatizer = ParserBuildGenerators(
            name='lemmatizer',
            input_cls=Token,
            output_cls=Lemma,

            skips=None,
            consecutive_outputs=False,

            strict_propagator=False,
            recursive=True,

            osd=Optimizer(
                branch_set=self._get_lemmatizer_branchset(operators),
                group_cls=TokenG
            ).data(strict_propagator=False)
        )

        classes = [build.get_class() for build in sorted(self.builds.values(), key=lambda build: -build.order)]

        materials = MODULE(
            name="materials",
            scope=[
                COMMENT("this module has been auto-generated by ItemEngine"),
                *self.__imports__,
                VAR("__all__").ASSIGN(LIST([STR(f"{cls.name!s}") for cls in classes] + [STR('build')])),
                *classes,
                self._generate_build_function()
            ]
        )

        engine = EngineBuildProcessFunctions(
            name=self.engine_name,
            input_cls=Char,
            output_cls=Lemma,

            text_input=True,
            strict_output=True,
            parsers=[tokenizer, lemmatizer],
            custom_modules=[materials]
        )

        return engine
