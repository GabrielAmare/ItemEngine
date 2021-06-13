from __future__ import annotations

from functools import reduce
from typing import List, Dict, Union, Tuple, Iterator

from python_generator import *

import item_engine as ie
import item_engine.textbase as tb
from item_engine import *
from item_engine.engine_builder import ParserBuildGenerators, EngineBuildProcessFunctions
from . import engine as gr


########################################################################################################################
# UTILS
########################################################################################################################

# TODO : set a function to identify the closest common super of two (or more) classes
# TODO : implement common variables for grouped operators into their most common group

class Class:
    def __init__(self, name: str):
        self.name: str = name
        self.direct_sups: List[Class] = []
        self.direct_subs: List[Class] = []

    def all_subs(self) -> Iterator[Class]:
        if self.direct_subs:
            for sub in self.direct_subs:
                yield from sub.all_subs()
        else:
            yield self

    def all_sups(self) -> Iterator[Class]:
        if self.direct_sups:
            for sup in self.direct_sups:
                yield from sup.all_sups()
        else:
            yield self

    def add_sup(self, sup: Class):
        assert sup not in self.direct_sups, 'duplicate'
        assert sup not in self.all_subs(), 'tautology'
        self.direct_sups.append(sup)
        sup.direct_subs.append(self)

    def add_sups(self, sups: Iterator[Class]):
        for sup in sups:
            self.add_sup(sup)

    def add_sub(self, sub: Class):
        assert sub not in self.direct_subs, 'duplicate'
        assert sub not in self.all_sups(), 'tautology'
        self.direct_subs.append(sub)
        sub.direct_sups.append(self)

    def add_subs(self, subs: Iterator[Class]):
        for sub in subs:
            self.add_sub(sub)

    @property
    def sub_order(self):
        """Return the bottom-up order of inheritance"""
        if self.direct_subs:
            return max(sub.sub_order for sub in self.direct_subs) + 1
        else:
            return 0

    @property
    def sup_order(self):
        """Return the top-bottom order of inheritance"""
        if self.direct_sups:
            return max(sub.sup_order for sub in self.direct_sups) + 1
        else:
            return 0

    @property
    def __CLASS__(self) -> CLASS:
        raise NotImplementedError


class GrammarWrapper:
    def __init__(self, ctx: Context, obj: gr.Grammar):
        self.ctx: Context = ctx
        self.obj: gr.Grammar = obj

        self.charsets: List[gr.Charset] = []
        self.operators: List[gr.Operator] = []
        self.groups: List[gr.Group] = []

        for arg in self.obj.args:
            self.register(arg)

    def register(self, obj):
        for cls, method in self.__class__.__register__.items():
            if type(obj) is cls:
                return method(self, obj)
        else:
            raise TypeError(f"the class {obj.__class__.__name__} is not handled by Grammar wrapper")

    def _register_charset(self, obj: gr.Charset):
        self.charsets.append(obj)

    def _register_group(self, obj: gr.Group):
        self.groups.append(obj)

    def _register_operator(self, obj: gr.Operator):
        self.operators.append(obj)

    __register__ = {
        gr.Charset: _register_charset,
        gr.Group: _register_group,
        gr.Operator: _register_operator,
    }


class Charset:
    def __init__(self, ctx: Context, obj: gr.Charset):
        self.ctx: Context = ctx
        self.obj: gr.Charset = obj

    @property
    def expr(self) -> str:
        expr = ''
        for arg in self.obj.args:
            if isinstance(arg, gr.Str):
                expr += eval(arg.expr)
            elif isinstance(arg, gr.Var):
                expr += self.ctx.get_charset(arg.name).expr
            else:
                raise TypeError(type(arg))
        return ''.join(sorted(set(expr)))

    @property
    def char_group(self) -> tb.CharG:
        return tb.charset(self.expr)


class Pattern:
    def __init__(self, ctx: Context, pattern: gr.Pattern):
        self.ctx: Context = ctx
        self.pattern: gr.Pattern = pattern

    @property
    def tokenizer_rule(self) -> ie.Rule:
        return ie.All.join(arg.tokenizer_rule for arg in self.pattern.args)

    @property
    def tokenizer_branch(self) -> ie.Branch:
        return Branch(
            name=self.pattern.name,
            rule=self.tokenizer_rule,
            priority=0
        )


class Operator(Class):
    def __init__(self, context: Context, operator: gr.Operator):
        super().__init__(name=operator.name)

        self.context: Context = context
        self.operator: gr.Operator = operator

        self.var_list: List[VAR] = self.context.var_list(self.operator)
        self.sign: Dict[str, Tuple[str, bool]] = self.context.var_dict(self.operator)

    @property
    def __INIT__(self) -> DEF:
        return DEF(
            name='__init__',
            args=ARGS(SELF, *[var.ARG() for var in self.var_list]),
            block=[
                SELF.SETATTR(var.name, var, t=var.t) for var in self.var_list
            ]
        )

    @property
    def __STR__(self) -> DEF:
        return DEF(
            name='__str__',
            args=ARGS(SELF),
            block=BLOCK(
                RETURN(self.context._str(self.operator))
            )
        )

    @property
    def __REPR__(self) -> DEF:
        return DEF(
            name='__repr__',
            args=ARGS(SELF),
            block=BLOCK(
                RETURN(FSTR(
                    "{self.__class__.__qualname__}(" +
                    ", ".join(f"{{self.{var.name}!r}}" for var in self.var_list) +
                    ")"
                ))
            )
        )

    @property
    def __EQ__(self) -> DEF:
        conditions = [SELF.GETATTR(var.name).EQ(VAR("other").GETATTR(var.name)) for var in self.var_list]
        return DEF(
            name='__eq__',
            args=ARGS(SELF, VAR("other")),
            block=BLOCK(IF(
                VAR("type").CALL(SELF).IS(VAR("type").CALL(VAR("other"))),
                BLOCK(
                    RETURN(reduce(AND, conditions))
                ), ELSE(
                    RETURN(VAR("NotImplemented"))
                )
            ))
        )

    @property
    def __MRO__(self):
        return sorted([sup.name for sup in self.direct_sups]) or None

    @property
    def __CLASS__(self) -> CLASS:
        return CLASS(
            name=self.operator.name,
            herits=self.__MRO__,
            block=[
                self.__INIT__,
                self.__STR__,
                self.__REPR__,
                self.__EQ__,
                VAR("__hash__").ASSIGN(NONE)
            ]
        )

    def get_builder(self, builder: OBJECT, obj: VAR) -> BLOCK:
        cls = VAR(self.operator.name)

        args = []

        for k, v in self.sign.items():
            t, m = v
            param = VAR(k)
            value = obj.GETATTR("data").GETITEM(STR(k))
            if m:
                value = VAR("list").CALL(VAR("map").CALL(builder, value))
            else:
                value = builder.CALL(value)
            args.append(param.ARG(value))

        return BLOCK(RETURN(cls.CALL(*args)))


class Group(Class):
    def __init__(self, context: Context, group: gr.Group):
        super().__init__(name=group.name)
        self.context: Context = context
        self.group: gr.Group = group

    @property
    def __MRO__(self):
        return sorted([sup.name for sup in self.direct_sups]) or None

    @property
    def __CLASS__(self) -> CLASS:
        return CLASS(
            name=self.group.name,
            herits=self.__MRO__,
            block=[

            ]
        )


class MethodRegister:
    class Wrapper:
        __cache__: List[MethodRegister.Wrapper] = []

        def __init__(self, method: callable):
            self.target: type = eval(method.__annotations__['obj'])
            self.method: callable = method

            MethodRegister.Wrapper.__cache__.append(self)

    @classmethod
    def __method_register(cls, data: List[Tuple[type, callable]]) -> callable:
        def function(self, obj):
            for type_, method in data:
                if isinstance(obj, type_):
                    return method(self, obj)
            else:
                raise TypeError(type(obj))

        return function

    def __init_subclass__(cls, **kwargs):
        cls._register: Dict[str, List[Tuple[type, callable]]] = {}

        for obj in cls.Wrapper.__cache__:
            name = obj.method.__name__
            cls._register.setdefault(name, [])
            cls._register[name].append((obj.target, obj.method))

        for name, data in cls._register.items():
            setattr(cls, name, cls.__method_register(data))

        cls.Wrapper.__cache__ = []

    wrap = Wrapper


MR = MethodRegister


class Context(MR):
    ####################################################################################################################
    # BASE
    ####################################################################################################################

    def __init__(self,
                 grammar: gr.Grammar,
                 patterns: List[Branch] = None,
                 symbol_table: Dict[str, str] = None,
                 skips: List[str] = None
                 ):
        self.whitespace: str = ''.join(sorted(set(eval(grammar.whitespace))))
        self.symbol_table: Dict[str, str] = symbol_table or {}
        self.skips: List[str] = skips or []

        self.grammar: gr.Grammar = grammar
        self.patterns: List[Branch] = patterns or []

        self._patterns: Dict[str, Pattern] = {}

        self.charsets: Dict[str, Charset] = {}
        self.operators: Dict[str, Operator] = {}
        self.groups: Dict[str, Group] = {}

        self.imports: List[IMPORT.FROM] = []

        self._register_all()
        self._build_groups()

    def _build_groups(self) -> None:
        for w_group in self.groups.values():
            for name in w_group.group.names:
                w_sub = self._get_class(name)
                if w_sub:
                    w_group.add_sub(w_sub)
                else:
                    raise Exception(f"group `{w_group.group.name!s}` is a super of undefined `{name!s}`")

    def _register_all(self) -> None:
        for o in self.grammar.args:
            self._register_one(o)

    def _register_one(self, o: gr.GrammarArg) -> None:
        t = type(o)

        if isinstance(o, gr.Operator):
            self.operators[o.name] = Operator(self, o)
        elif isinstance(o, gr.Charset):
            self.charsets[o.name] = Charset(self, o)
        elif isinstance(o, gr.Pattern):
            self._patterns[o.name] = Pattern(self, o)
        elif isinstance(o, gr.Group):
            self.groups[o.name] = Group(self, o)
        else:
            raise TypeError(t)

    def get_charset(self, name: str) -> Charset:
        for charset_name, w_charset in self.charsets.items():
            if charset_name == name:
                return w_charset

    def _get_operator(self, name: str) -> Operator:
        for operator_name, w_operator in self.operators.items():
            if operator_name == name:
                return w_operator

    def _get_group(self, name: str) -> Group:
        for group_name, w_group in self.groups.items():
            if group_name == name:
                return w_group

    def _get_class(self, name: str) -> Class:
        group = self._get_group(name)
        if group:
            return group

        operator = self._get_operator(name)
        if operator:
            return operator

    ####################################################################################################################
    # STR
    ####################################################################################################################

    @MR.wrap
    def _str(self, obj: gr.Str) -> EXPRESSION:
        return STR(eval(obj.expr))

    @MR.wrap
    def _str(self, obj: gr.O_MatchAs) -> EXPRESSION:
        return VAR("str").CALL(SELF.GETATTR(obj.key))

    @MR.wrap
    def _str(self, obj: gr.O_MatchIn) -> EXPRESSION:
        return VAR("map").CALL(VAR("str"), SELF.GETATTR(obj.key))

    @MR.wrap
    def _str(self, obj: gr.O_All) -> EXPRESSION:
        arg, *args = map(self._str, obj.args)
        for new in args:
            arg = ADD(arg, new)
        return arg

    @MR.wrap
    def _str(self, obj: gr.Operator) -> EXPRESSION:
        return self._str(obj.args[0])

    @MR.wrap
    def _str(self, obj: gr.O_Enum) -> EXPRESSION:
        sep = self._str(obj.separator)
        if isinstance(sep, OBJECT):
            return sep.METH("join", self._str(obj.child))
        else:
            raise NotImplementedError

    @MR.wrap
    def _str(self, obj: gr.O_EnumP) -> EXPRESSION:
        sep = self._str(obj.separator)
        if isinstance(sep, OBJECT):
            return sep.METH("join", self._str(obj.child))
        else:
            raise NotImplementedError

    ####################################################################################################################
    # VARS
    ####################################################################################################################
    @MR.wrap
    def var_dict(self, obj: gr.O_MatchAs) -> Dict[str, Tuple[str, bool]]:
        return {obj.key: (obj.name, False)}

    @MR.wrap
    def var_dict(self, obj: gr.O_MatchIn) -> Dict[str, Tuple[str, bool]]:
        return {obj.key: (obj.name, True)}

    @MR.wrap
    def var_dict(self, obj: gr.O_All) -> Dict[str, Tuple[str, bool]]:
        data: Dict[str, Tuple[str, bool]] = {}

        for arg in obj.args:
            for k, v in self.var_dict(arg).items():
                if k in data:
                    if data[k] != v:
                        raise Exception("variable definition ambiguity")

                    if not data[k][1]:
                        raise Exception("cannot re-use a single value variable")

                data[k] = v

        return data

    @MR.wrap
    def var_dict(self, obj: gr.O_Enum) -> Dict[str, Tuple[str, bool]]:
        return self.var_dict(obj.child)

    @MR.wrap
    def var_dict(self, obj: gr.O_EnumP) -> Dict[str, Tuple[str, bool]]:
        return self.var_dict(obj.child)

    @MR.wrap
    def var_dict(self, obj: gr.Operator) -> Dict[str, Tuple[str, bool]]:
        first, *args = obj.args
        res = self.var_dict(first)
        for arg in args:
            if res != self.var_dict(arg):
                raise Exception("different variables signature in Operator is not allowed")
        return res

    @MR.wrap
    def var_dict(self, obj: gr.Str) -> Dict[str, Tuple[str, bool]]:
        return {}

    def var_list(self, obj) -> List[VAR]:
        result: List[VAR] = []
        for k, v in self.var_dict(obj).items():
            t, m = v
            result.append(VAR(k, t=f"List[{t}]" if m else t))
        return result

    ####################################################################################################################
    # STRINGS
    ####################################################################################################################

    def _str_expr(self, obj: gr.Str) -> str:
        return eval(obj.expr).strip(self.whitespace)

    def _str_name(self, obj: gr.Str) -> str:
        name = self._str_expr(obj)
        for key, val in self.symbol_table.items():
            name = name.replace(key, val)
        return name

    ####################################################################################################################
    # TOKENIZER
    ####################################################################################################################

    @MR.wrap
    def _tokenizer_rule(self, obj: gr.Str) -> ie.Rule:
        return tb.string(eval(obj.expr))

    @MR.wrap
    def _tokenizer_rule(self, obj: gr.Var) -> ie.Rule:
        charset = self.get_charset(obj.name)
        if charset:
            return tb.charset(charset.expr).inc()

        raise ValueError(obj)

    @MR.wrap
    def _tokenizer_rule(self, obj: gr.P_Inv) -> ie.Rule:
        charset = self.get_charset(obj.arg.name)
        if charset:
            return (~tb.charset(charset.expr)).inc()

        raise ValueError(obj)

    @MR.wrap
    def _tokenizer_rule(self, obj: gr.P_Optional) -> ie.Rule:
        return self._tokenizer_rule(obj.arg).optional

    @MR.wrap
    def _tokenizer_rule(self, obj: gr.P_RepeatP) -> ie.Rule:
        return self._tokenizer_rule(obj.arg).repeat(1, ie.INF)

    @MR.wrap
    def _tokenizer_rule(self, obj: gr.P_Repeat) -> ie.Rule:
        return self._tokenizer_rule(obj.arg).repeat(0, ie.INF)

    @MR.wrap
    def _tokenizer_rule(self, obj: gr.P_Inv_) -> ie.Rule:
        raise NotImplementedError

    @MR.wrap
    def _tokenizer_rule(self, obj: gr.P_All) -> ie.Rule:
        return ie.All.join(map(self._tokenizer_rule, obj.args))

    @MR.wrap
    def _tokenizer_rule(self, obj: gr.Pattern) -> ie.Rule:
        return ie.Any.join(map(self._tokenizer_rule, obj.args))

    @MR.wrap
    def _tokenizer_branches(self, obj: gr.Operator) -> Iterator[Branch]:
        for arg in obj.args:
            yield from self._tokenizer_branches(arg)

    @MR.wrap
    def _tokenizer_branches(self, obj: gr.O_All) -> Iterator[Branch]:
        for arg in obj.args:
            yield from self._tokenizer_branches(arg)

    @MR.wrap
    def _tokenizer_branches(self, obj: gr.O_Enum) -> Iterator[Branch]:
        yield from self._tokenizer_branches(obj.separator)

    @MR.wrap
    def _tokenizer_branches(self, obj: gr.O_EnumP) -> Iterator[Branch]:
        yield from self._tokenizer_branches(obj.separator)

    @MR.wrap
    def _tokenizer_branches(self, obj: gr.Str) -> Iterator[Branch]:
        expr = self._str_expr(obj)
        if expr:
            name = self._str_name(obj)
            yield Branch(
                name=name,
                rule=tb.string(expr),
                priority=100 + len(expr)
            )

    @MR.wrap
    def _tokenizer_branches(self, obj: gr.Pattern) -> Iterator[Branch]:
        yield ie.Branch(
            name=obj.name,
            rule=self._tokenizer_rule(obj),
            priority=0
        )

    def _tokenizer_branchset(self) -> Union[BranchSet, Branch]:
        branches = [
            Branch(
                name="WHITESPACE",
                rule=tb.charset(self.whitespace).inc().repeat(1, INF),
                priority=0
            ),
            *self.patterns
        ]

        for w_pattern in self._patterns.values():
            branches.extend(self._tokenizer_branches(w_pattern.pattern))

        for w_operator in self.operators.values():
            branches.extend(self._tokenizer_branches(w_operator.operator))

        return BranchSet.make(*branches) if branches else None

    ####################################################################################################################
    # LEMMATIZER
    ###################################################################################################################

    def _token_group(self, name: str) -> tb.TokenG:
        """Return the token group associated with a name"""
        cls = self._get_class(name)
        names = [sub.name for sub in cls.all_subs()] if cls else [name]
        return tb.TokenG(map(tb.TokenI, names)) / tb.TokenG({tb.TokenI(name='EOF')})

    def _lemmatizer_rule_All(self, obj: gr.O_All) -> Rule:
        return All.join(map(self._lemmatizer_rule, obj.args))

    def _lemmatizer_rule_Str(self, obj: gr.Str) -> Rule:
        name = self._str_name(obj)
        if name:
            return Match(group=tb.TokenG({tb.TokenI(name=name)}) / tb.TokenG({tb.TokenI(name='EOF')}), action=INCLUDE)
        else:
            return VALID

    def _lemmatizer_rule_Match(self, obj: gr.O_Match) -> Rule:
        return Match(group=self._token_group(obj.name), action=INCLUDE)

    def _lemmatizer_rule_MatchAs(self, obj: gr.O_MatchAs) -> Rule:
        return Match(group=self._token_group(obj.name), action=INCLUDE_AS.format(obj.key))

    def _lemmatizer_rule_MatchIn(self, obj: gr.O_MatchIn) -> Rule:
        return Match(group=self._token_group(obj.name), action=INCLUDE_IN.format(obj.key))

    def _lemmatizer_rule_Enum(self, obj: gr.O_Enum) -> Rule:
        # OPTIONAL [1, INF]
        child_rule = self._lemmatizer_rule(obj.child)
        separator = self._lemmatizer_rule(obj.separator)
        if separator == VALID:
            return child_rule.repeat(1, INF)
        else:
            return child_rule & (separator & child_rule).repeat(0, INF)

    def _lemmatizer_rule_EnumP(self, obj: gr.O_EnumP) -> Rule:
        # REQUIRED [2, INF]
        child_rule = self._lemmatizer_rule(obj.child)
        separator = self._lemmatizer_rule(obj.separator)
        if separator == VALID:
            return child_rule.repeat(2, INF)
        else:
            return child_rule & (separator & child_rule).repeat(1, INF)

    def _lemmatizer_rule(self, obj) -> Rule:
        if isinstance(obj, gr.O_All):
            return self._lemmatizer_rule_All(obj)
        elif isinstance(obj, gr.Str):
            return self._lemmatizer_rule_Str(obj)
        elif isinstance(obj, gr.O_Match):
            return self._lemmatizer_rule_Match(obj)
        elif isinstance(obj, gr.O_MatchAs):
            return self._lemmatizer_rule_MatchAs(obj)
        elif isinstance(obj, gr.O_MatchIn):
            return self._lemmatizer_rule_MatchIn(obj)
        elif isinstance(obj, gr.O_Enum):
            return self._lemmatizer_rule_Enum(obj)
        elif isinstance(obj, gr.O_EnumP):
            return self._lemmatizer_rule_EnumP(obj)
        else:
            raise TypeError(type(obj))

    def _lemmatizer_branchset(self) -> Union[BranchSet, Branch]:
        branches = []
        for name, w_operator in self.operators.items():
            branches.append(
                Branch(
                    name=name,
                    rule=self._lemmatizer_rule(w_operator.operator),
                    priority=w_operator.sup_order
                )
            )

        return BranchSet.make(*branches) if branches else None

    ####################################################################################################################
    # BUILD FUNC
    ####################################################################################################################

    def _generate_build_function(self) -> DEF:
        obj = VAR("obj")
        input_args = [obj.ARG()]

        operators: List[Operator] = sorted(self.operators.values(), key=lambda operator: -operator.sub_order)

        obj = VAR("obj")
        builder = VAR("build")

        self.imports.append(IMPORT.TYPE(tb.Token))
        self.imports.append(IMPORT.TYPE(tb.Lemma))

        operator_switch = SWITCH(cases=[
            (obj.GETATTR("value").EQ(STR(operator.name)), operator.get_builder(builder, obj))
            for operator in operators
        ], default=RAISE(VAR("ValueError").CALL(obj.GETATTR("value"))))

        switch = SWITCH(
            cases=[
                (ISINSTANCE(obj, VAR("Lemma")), operator_switch),
                (ISINSTANCE(obj, VAR("Token")), RETURN(obj.GETATTR("content")))
            ],
            default=RAISE(VAR("TypeError").CALL(VAR("type").CALL(obj)))
        )

        return DEF(name='build', args=input_args, block=switch)

    ####################################################################################################################
    # ENGINE
    ####################################################################################################################

    def _import_from(self, package: str, module: str):
        self.imports.append(IMPORT.FROM(package, module))

    def generate_engine(self) -> EngineBuildProcessFunctions:
        self._import_from("__future__", "annotations")

        tokenizer = ParserBuildGenerators(
            name='tokenizer',
            input_cls=tb.Char,
            output_cls=tb.Token,

            skips=["WHITESPACE"] + self.skips,
            consecutive_outputs=True,

            strict_propagator=True,
            recursive=False,

            osd=Optimizer(branch_set=self._tokenizer_branchset(), group_cls=tb.CharG).data(strict_propagator=True)

        )
        lemmatizer = ParserBuildGenerators(
            name='lemmatizer',
            input_cls=tb.Token,
            output_cls=tb.Lemma,

            skips=None,
            consecutive_outputs=False,

            strict_propagator=False,
            recursive=True,

            osd=Optimizer(branch_set=self._lemmatizer_branchset(), group_cls=tb.TokenG).data(strict_propagator=False)
        )

        group_classes: List[CLASS] = [
            group.__CLASS__
            for group in sorted(self.groups.values(), key=lambda group: -group.sub_order)
        ]
        operator_classes: List[CLASS] = [
            operator.__CLASS__
            for operator in sorted(self.operators.values(), key=lambda operator: -operator.sub_order)
        ]
        classes: List[CLASS] = group_classes + operator_classes

        materials = MODULE(
            name="materials",
            scope=[
                COMMENT("this module has been auto-generated by ItemEngine"),
                *self.imports,
                VAR("__all__").ASSIGN(LIST([STR(f"{cls.name!s}") for cls in classes] + [STR('build')])),
                *classes,
                self._generate_build_function()
            ]
        )

        engine = EngineBuildProcessFunctions(
            package_name='engine',
            wrapper_name='parse',
            input_cls=tb.Char,
            output_cls=tb.Lemma,

            text_input=True,
            strict_output=True,
            parsers=[tokenizer, lemmatizer],
            custom_modules=[materials]
        )

        return engine
