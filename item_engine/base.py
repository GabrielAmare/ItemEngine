from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from functools import reduce
from operator import and_, xor
from typing import Tuple, Iterator, FrozenSet, List, TypeVar, Type, Union, Hashable, Iterable

import python_generator as pg

from .constants import ACTION, INCLUDE, EXCLUDE, AS, IN, T_STATE, INDEX, STATE, CASE, NT_STATE, INF, EOF
from .utils import ArgsHashed

__all__ = [
    "Rule", "RuleUnit", "RuleList", "Empty",  # abstracts
    "Optional", "Repeat", "All", "Any",  # composed
    "Match", "VALID", "ERROR"  # simple
]


########################################################################################################################
# Rule
########################################################################################################################

class Rule(ArgsHashed, ABC):
    @classmethod
    def cast(cls, obj: RuleCast) -> Rule:
        if obj is True:
            return VALID

        if obj is False:
            return ERROR

        if isinstance(obj, (frozenset, set)):
            return Any.make(*obj)

        if isinstance(obj, (tuple, list)):
            return All.make(*obj)

        if isinstance(obj, Rule):
            return obj

        if isinstance(obj, Group):
            return Match(obj, INCLUDE)

        raise TypeError(type(obj))

    def __and__(self, other: Rule) -> Rule:
        return All.make(self, other)

    def __or__(self, other) -> Rule:
        return Any.make(self, other)

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    @property
    def is_skipable(self) -> bool:
        raise NotImplementedError

    @property
    def alphabet(self) -> FrozenSet[Item]:
        raise NotImplementedError

    @property
    def is_non_terminal(self) -> bool:
        raise NotImplementedError

    @property
    def is_terminal(self) -> bool:
        raise NotImplementedError

    @property
    def is_valid(self) -> bool:
        raise NotImplementedError

    @property
    def is_error(self) -> bool:
        raise NotImplementedError

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        raise NotImplementedError

    def repeat(self, mn: int = 0, mx: int = INF) -> Rule:
        assert mn >= 0
        assert mx == -1 or (mx >= mn and mx > 0)

        prefix = VALID if mn == 0 else All.join(self for _ in range(mn))
        suffix = Repeat.make(self) if mx == INF else All.join(self for _ in range(mx - mn))

        return All.make(prefix, suffix)

    @property
    def optional(self: Rule) -> Union[Skipable, Empty]:
        return Optional.make(self)


########################################################################################################################
# Empty | RuleUnit | RuleList
########################################################################################################################

class Empty(Rule):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.valid

    def __init__(self, valid: bool):
        self.valid: bool = valid

    def __repr__(self):
        return f"{self.__class__.__name__}({self.valid!r})"

    def __str__(self):
        return "VALID" if self.valid else "ERROR"

    alphabet: FrozenSet[Item] = frozenset()
    is_skipable: bool = False
    is_non_terminal: bool = False
    is_terminal: bool = True

    @property
    def is_valid(self) -> bool:
        return self.valid

    @property
    def is_error(self) -> bool:
        return not self.valid

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        yield Match(group=Group(inverted=self.valid), action=EXCLUDE), self


VALID = Empty(True)
ERROR = Empty(False)


class RuleUnit(Rule, ABC):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.rule

    def __init__(self, rule: Rule):
        self.rule: Rule = rule

    def __repr__(self):
        return f"{self.__class__.__name__}({self.rule!r})"

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return self.rule.alphabet


class RuleList(Rule, ABC):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), tuple(self.rules)

    def __init__(self, *rules: Rule):
        assert len(rules) > 1
        self.rules: List[Rule] = list(rules)

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(map(repr, self.rules))})"

    def __iter__(self) -> Iterator[Rule]:
        return iter(self.rules)

    def __len__(self) -> int:
        return len(self.rules)

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return frozenset({item for rule in self.rules for item in rule.alphabet})


class RuleSet(Rule, ABC):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), tuple(sorted(self.rules))

    def __init__(self, *rules: Rule):
        rules = frozenset(rules)
        assert len(rules) > 1
        self.rules: FrozenSet[Rule] = rules

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(map(repr, self.rules))})"

    def __iter__(self) -> Iterator[Rule]:
        return iter(sorted(self.rules))

    def __len__(self) -> int:
        return len(self.rules)

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return frozenset({item for rule in self.rules for item in rule.alphabet})


########################################################################################################################
# Optional | Repeat | All | Any
########################################################################################################################

class Skipable(RuleUnit, ABC):
    is_skipable: bool = True
    is_non_terminal: bool = True
    is_terminal: bool = False
    is_valid: bool = False
    is_error: bool = False

    @classmethod
    def make(cls, rule: RuleCast) -> Union[Skipable, Empty]:
        rule: Rule = Rule.cast(rule)

        if isinstance(rule, Repeat):
            return rule

        if isinstance(rule, Empty):
            return VALID

        if isinstance(rule, Optional):
            rule = rule.rule

        return cls(rule)


class Optional(Skipable):
    def __init__(self, rule: Rule):
        assert not isinstance(rule, (Skipable, Empty))
        super().__init__(rule)

    def __str__(self):
        return f"?[ {self.rule!s} ]"

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for first, after in self.rule.splited:
            yield first, after


class Repeat(Skipable):
    def __init__(self, rule: Rule):
        assert not isinstance(rule, (Skipable, Empty))
        super().__init__(rule)

    def __str__(self):
        return f"*[ {self.rule!s} ]"

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for first, after in self.rule.splited:
            yield first, after & self


class All(RuleList):
    @classmethod
    def join(cls, args: Iterable[RuleCast]) -> Rule:
        return cls.make(*args)

    @classmethod
    def _flat(cls, *args: RuleCast) -> Iterable[Rule]:
        for arg in args:
            arg: Rule = Rule.cast(arg)

            if isinstance(arg, cls):
                yield from cls._flat(*arg.rules)
            else:
                yield arg

    @classmethod
    def make(cls, *args: RuleCast) -> Rule:
        rules: List[Rule] = []

        for arg in cls._flat(*args):
            if arg == ERROR:
                return ERROR

            if arg == VALID:
                continue

            rules.append(arg)

        if len(rules) == 0:
            return VALID

        if len(rules) == 1:
            return rules[0]

        return cls(*rules)

    def __init__(self, *rules: Rule):
        assert not any(isinstance(rule, All) for rule in rules)
        assert not any(isinstance(rule, Empty) for rule in rules)
        super().__init__(*rules)

    @property
    def decompose(self) -> Iterator[Tuple[Rule, Rule]]:
        for index, rule in enumerate(self.rules):
            if index + 1 < len(self.rules):
                yield rule, reduce(and_, self.rules[index + 1:])
            else:
                yield rule, VALID

            if not rule.is_skipable:
                break

    @property
    def is_skipable(self) -> bool:
        return all(rule.is_skipable for rule in self)

    @property
    def is_non_terminal(self) -> bool:
        return len(self) != 1 or self.rules[0].is_non_terminal

    @property
    def is_terminal(self) -> bool:
        return len(self) == 1 and self.rules[0].is_terminal

    @property
    def is_valid(self) -> bool:
        return len(self) == 1 and self.rules[0].is_valid

    @property
    def is_error(self) -> bool:
        return len(self) == 1 and self.rules[0].is_error

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for rule_first, rule_after in self.decompose:
            for first, after in rule_first.splited:
                yield first, after & rule_after

    def __str__(self):
        return " & ".join(map(str, self))


class Any(RuleSet):
    @classmethod
    def join(cls, args: Iterable[RuleCast]):
        return cls.make(*args)

    @classmethod
    def _flat(cls, *args: RuleCast) -> Iterable[Rule]:
        for arg in args:
            arg: Rule = Rule.cast(arg)

            if isinstance(arg, cls):
                yield from cls._flat(*arg.rules)
            else:
                yield arg

    @classmethod
    def make(cls, *args: RuleCast):
        rules: List[Rule] = []

        for arg in cls._flat(*args):
            if arg == ERROR:
                continue

            if arg == VALID:
                return VALID

            if arg not in rules:
                rules.append(arg)

        if len(rules) == 0:
            return ERROR

        if len(rules) == 1:
            return rules[0]

        return cls(*rules)

    def __init__(self, *rules: Rule):
        assert not any(isinstance(rule, Any) for rule in rules)
        assert not any(isinstance(rule, Empty) for rule in rules)
        super().__init__(*rules)

    def __str__(self):
        return " | ".join(map(str, self))

    @property
    def is_skipable(self) -> bool:
        return any(rule.is_skipable for rule in self)

    @property
    def is_non_terminal(self) -> bool:
        return any(rule.is_non_terminal for rule in self)

    @property
    def is_terminal(self) -> bool:
        return all(rule.is_terminal for rule in self)

    @property
    def is_valid(self) -> bool:
        return all(rule.is_valid for rule in self)

    @property
    def is_error(self) -> bool:
        return all(rule.is_error for rule in self)

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for rule in self:
            for first, after in rule.splited:
                yield first, after


########################################################################################################################
# Match
########################################################################################################################


class Match(Rule):
    is_skipable: bool = False
    is_non_terminal: bool = True
    is_terminal: bool = False
    is_valid: bool = False
    is_error: bool = False

    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.group, self.action

    def __init__(self, group: Group, action: ACTION = ""):
        self.group: Group = group
        self.action: ACTION = action

    def __repr__(self):
        return f"{self.__class__.__name__}({self.group!r}, {self.action!r})"

    def __str__(self):
        return f"{self.group!s}({self.action!s})"

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return self.group.items

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        yield self, VALID
        yield Match(~self.group, EXCLUDE), ERROR


__all__ += ["Item", "Group"]


class ItemInterface(ArgsHashed, ABC):
    def match(self, action: ACTION) -> Match:
        if isinstance(self, Item):
            return Match(self.as_group, action)
        elif isinstance(self, Group):
            return Match(self, action)
        else:
            raise ValueError(self)

    def include(self) -> Match:
        return self.match(INCLUDE)

    def exclude(self) -> Match:
        return self.match(EXCLUDE)

    def include_as(self, key: str) -> Match:
        return self.match(AS.format(key))

    def include_in(self, key: str) -> Match:
        return self.match(IN.format(key))

    inc = include
    exc = exclude
    as_ = include_as
    in_ = include_in


class Item(ItemInterface, ABC):
    @property
    def as_group(self) -> Group:
        raise NotImplementedError

    def __or__(self, other: Group) -> Group:
        return self.as_group | other

    __ior__ = __or__

    def __add__(self, other: Item) -> Group:
        return self.as_group + other

    __iadd__ = __add__


E = TypeVar("E", bound=Item)
T = TypeVar("T")


class Group(ItemInterface, ArgsHashed, ABC):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.inverted, tuple(sorted(self.items))

    @classmethod
    def never(cls: Type[T]) -> T:
        """return ∅"""
        return cls(frozenset(), False)

    @classmethod
    def always(cls: Type[T]) -> T:
        """return Ω"""
        return cls(frozenset(), True)

    @property
    def is_never(self) -> bool:
        """return self == ∅"""
        return not self.inverted and not self.items

    @property
    def is_always(self) -> bool:
        """return self == Ω"""
        return self.inverted and not self.items

    def __init__(self, items: Iterable[Item] = None, inverted: bool = False):
        self.items: FrozenSet[Item] = frozenset() if items is None else frozenset(items)
        self.inverted: bool = inverted

    def __repr__(self) -> str:
        """return repr(self)"""
        return f"{self.__class__.__name__}({self.items!r}, {self.inverted!r})"

    @property
    def items_str(self) -> str:
        return str(self.items)

    def __str__(self) -> str:
        """return str(self)"""
        if self.items:
            return f"{'¬' if self.inverted else ''}{self.items_str}"
        else:
            return 'Ω' if self.inverted else '∅'

    def __contains__(self, item) -> bool:
        return xor(item in self.items, self.inverted)

    def __invert__(self: T) -> T:
        return self.__class__(self.items, not self.inverted)

    def __or__(self: T, other: T) -> T:
        if other.inverted:
            func = frozenset.intersection if self.inverted else frozenset.difference
            return self.__class__(func(other.items, self.items), True)
        else:
            func = frozenset.difference if self.inverted else frozenset.union
            return self.__class__(func(self.items, other.items), self.inverted)

    def __and__(self: T, other: T) -> T:
        if other.inverted:
            func = frozenset.union if self.inverted else frozenset.difference
            return self.__class__(func(self.items, other.items), self.inverted)
        else:
            func = frozenset.difference if self.inverted else frozenset.intersection
            return self.__class__(func(other.items, self.items), False)

    def __truediv__(self: T, other: T) -> T:
        if other.inverted:
            func = frozenset.difference if self.inverted else frozenset.intersection
            return self.__class__(func(other.items, self.items), False)
        else:
            func = frozenset.union if self.inverted else frozenset.difference
            return self.__class__(func(self.items, other.items), self.inverted)

    def __add__(self: T, other: Item) -> T:
        func = self.items.difference if self.inverted else self.items.union
        return self.__class__(func({other}), self.inverted)

    def __sub__(self: T, other: Item) -> T:
        func = self.items.union if self.inverted else self.items.difference
        return self.__class__(func({other}), self.inverted)

    __iand__ = __and__
    __ior__ = __or__
    __itruediv__ = __truediv__
    __iadd__ = __add__
    __isub__ = __sub__

    @property
    def code_factory(self) -> Type[pg.CONDITION]:
        if len(self.items) == 1:
            if self.inverted:
                return pg.NE
            else:
                return pg.EQ
        else:
            if self.inverted:
                return pg.NOT_IN
            else:
                return pg.IN

    def condition(self, item: pg.VAR) -> pg.CONDITION:
        raise NotImplementedError


__all__ += ["Branch", "BranchSet"]


########################################################################################################################
# Branch & BranchSet
########################################################################################################################

class Branch(RuleUnit):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.name, self.rule, self.priority

    def __init__(self, name: str, rule: Rule, priority: int = 0):
        assert not isinstance(rule, Branch)
        super().__init__(rule)
        self.name: str = name
        self.priority: int = priority

    def new_rule(self, rule: Rule) -> Branch:
        return Branch(self.name, rule, self.priority)

    def __str__(self):
        return f"{self.name!s}[{self.priority}] : {self.rule!s}"

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return self.rule.alphabet

    @property
    def is_skipable(self) -> bool:
        return self.rule.is_skipable

    @property
    def is_non_terminal(self) -> bool:
        return self.rule.is_non_terminal

    @property
    def is_terminal(self) -> bool:
        return self.rule.is_terminal

    @property
    def is_valid(self) -> bool:
        return self.rule.is_valid

    @property
    def is_error(self) -> bool:
        return self.rule.is_error

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for first, after in self.rule.splited:
            yield first, after

        if self.rule.is_skipable:
            yield Match(group=Group.always(), action=EXCLUDE), VALID


class BranchSet(ArgsHashed):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), tuple(sorted(self.branches))

    def __init__(self, branches: Iterable[Branch] = None):
        if branches is None:
            branches = frozenset()
        self.branches: FrozenSet[Branch] = frozenset(branches)

    def __bool__(self):
        return bool(self.branches)

    def terminal_code(self, throw_errors: bool = False) -> Iterator[T_STATE]:
        valid_branches = [branch for branch in self.branches if branch.is_valid]
        valid_max_priority = max([branch.priority for branch in valid_branches], default=0)
        valid_names = [T_STATE(branch.name) for branch in valid_branches if branch.priority == valid_max_priority]

        if valid_names:
            return valid_names

        error_branches = [branch for branch in self.branches if branch.is_error]
        error_max_priority = max([branch.priority for branch in error_branches], default=0)
        error_names = [branch.name for branch in error_branches if branch.priority == error_max_priority]

        if error_names:
            if throw_errors:
                return []
            else:
                if error_names:
                    return [T_STATE("!" + "|".join(error_names))]
                else:
                    return [T_STATE("!")]

    def get_all_cases(self) -> Iterator[Tuple[Group, ACTION, Branch]]:
        for branch in self.branches:
            for first, after in branch.splited:
                yield first.group, first.action, branch.new_rule(after)

    @property
    def only_non_terminals(self) -> BranchSet:
        """Remove the terminal branches"""
        return BranchSet(frozenset(branch for branch in self.branches if not branch.is_terminal))

    @property
    def only_valids(self) -> BranchSet:
        """Remove the terminal branches"""
        return BranchSet(frozenset(branch for branch in self.branches if branch.is_valid))

    @property
    def only_errors(self) -> BranchSet:
        """Remove the terminal branches"""
        return BranchSet(frozenset(branch for branch in self.branches if branch.is_error))

    def truncated(self, formal: bool):
        if formal:
            valid_part = self.only_valids
            error_part = self.only_errors
            non_terminal_part = self.only_non_terminals
            return non_terminal_part or valid_part or error_part
        else:
            return self

    @property
    def is_non_terminal(self) -> bool:
        return any(branch.is_non_terminal for branch in self.branches)

    @property
    def is_terminal(self) -> bool:
        return all(branch.is_terminal for branch in self.branches)

    @property
    def is_valid(self) -> bool:
        return all(branch.is_valid for branch in self.branches)

    @property
    def is_error(self) -> bool:
        return all(branch.is_error for branch in self.branches)

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return frozenset({item for branch in self.branches for item in branch.alphabet})


__all__ += ["Element", "OPTIONS"]


########################################################################################################################
# Element
########################################################################################################################

@dataclass(frozen=True, order=True)
class HasSpan:
    at: INDEX
    to: INDEX

    @property
    def span(self) -> Tuple[INDEX, INDEX]:
        return self.at, self.to

    def lt(self, other: HasSpan) -> bool:
        return self.to < other.at

    def le(self, other: HasSpan) -> bool:
        return self.to <= other.at

    def gt(self, other: HasSpan) -> bool:
        return self.to > other.at

    def ge(self, other: HasSpan) -> bool:
        return self.to >= other.at

    def eq(self, other: HasSpan) -> bool:
        return self.at == other.at and self.to == other.to

    def ne(self, other: HasSpan) -> bool:
        return self.at != other.at or self.to != other.to

    def ol(self, other: HasSpan) -> bool:
        if other.at < self.to:
            return other.to > self.at
        elif other.at > self.to:
            return other.to < self.at
        else:
            return False


@dataclass(frozen=True, order=True)
class Element(HasSpan):
    value: STATE

    @classmethod
    def EOF(cls, at: INDEX):
        return cls(at=at, to=at, value=T_STATE(EOF))

    def develop(self, case: CASE, item: Element) -> Element:
        raise NotImplementedError

    def eof(self):
        return self.__class__.EOF(self.to)

    @property
    def is_eof(self):
        return self.value == EOF

    @property
    def is_non_terminal(self) -> bool:
        return isinstance(self.value, NT_STATE)

    @property
    def is_terminal(self) -> bool:
        return isinstance(self.value, T_STATE)

    @property
    def is_valid(self) -> bool:
        return self.is_terminal and not self.value.startswith('!')

    @property
    def is_error(self) -> bool:
        return self.is_terminal and self.value.startswith('!')


class OPTIONS:
    @staticmethod
    def ordered(elements: List[Element]) -> bool:
        """Return True when elements are in order, it implies that there's no overlapping"""
        return all(a.le(b) for a, b in zip(elements, elements[1:]))

    @staticmethod
    def consecutive(elements: List[Element]) -> bool:
        """Return True when elements are in order and conscutive, it implies that there's no overlapping"""
        return all(a.to == b.at for a, b in zip(elements, elements[1:]))

    @staticmethod
    def ordered_layers(layers: List[List[Element]]) -> bool:
        """Return True when elements from consecutive layers are in order (for all possible pairs)"""
        return all(all(a.le(b) for a in A for b in B) for A, B in zip(layers, layers[1:]))

    @staticmethod
    def simultaneous_end(elements: List[Element]) -> bool:
        return all(a.to == b.to for a in elements for b in elements)

    @staticmethod
    def simultaneous_start(elements: List[Element]) -> bool:
        return all(a.at == b.at for a in elements for b in elements)

    @staticmethod
    def non_overlaping(elements: List[Element]):
        return all(not a.ol(b) for a in elements for b in elements if a is not b)


RuleCast = Union[bool, frozenset, set, tuple, list, Group, Rule]
