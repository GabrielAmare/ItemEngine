from __future__ import annotations

from abc import ABC
from functools import reduce
from operator import and_
from typing import Tuple, Iterator, FrozenSet, List, Union, Hashable, Iterable, Collection, TypeVar, Generic

from .constants import ACTION, INCLUDE, EXCLUDE, INF
from .items import Item, Group
from .utils import ArgsHashed

__all__ = [
    "Rule", "RuleUnit", "RuleList", "Empty",  # abstracts
    "Optional", "Repeat", "All", "Any",  # composed
    "Match", "VALID", "ERROR",  # simple
    "Branch", "BranchSet"  # top-level
]


class Rule(ArgsHashed, ABC):
    @classmethod
    def cast(cls, obj: RuleCast) -> Rule:
        if isinstance(obj, Rule):
            return obj

        if isinstance(obj, Item):
            return Match(obj.as_group, INCLUDE)

        if isinstance(obj, Group):
            return Match(obj, INCLUDE)

        if obj is True:
            return VALID

        if obj is False:
            return ERROR

        if isinstance(obj, (frozenset, set)):
            return Any.make(*obj)

        if isinstance(obj, (tuple, list)):
            return All.make(*obj)

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


T = TypeVar("T", bound=Rule)


class RuleLeaf(Rule, ABC):
    """A RuleLeaf contains 0 sub-rule"""


class RuleUnit(Rule, Generic[T], ABC):
    """A RuleLeaf contains 1 sub-rule"""

    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.rule

    def __init__(self, rule: T):
        self.rule: T = rule

    def __repr__(self):
        return f"{self.__class__.__name__}({self.rule!r})"

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return self.rule.alphabet


class RuleColl(Rule, Generic[T], ABC):
    """A RuleLeaf contains 2 or more sub-rules"""
    rules: Collection[T]

    def __init__(self, rules: Collection[T]):
        assert len(rules) > 1
        self.rules: Collection[T] = rules

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(map(repr, self))})"

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return frozenset({item for branch in self.rules for item in branch.alphabet})

    def __len__(self) -> int:
        return len(self.rules)

    def __iter__(self) -> Iterator[T]:
        raise NotImplementedError


class RuleList(RuleColl[T], Generic[T], ABC):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), tuple(self.rules)

    def __init__(self, *rules: T):
        super().__init__(list(rules))

    def __iter__(self) -> Iterator[T]:
        return iter(self.rules)


class RuleSet(RuleColl[T], Generic[T], ABC):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), tuple(sorted(self.rules))

    def __init__(self, *rules: T):
        rules = frozenset(rules)
        super().__init__(frozenset(rules))

    def __iter__(self) -> Iterator[T]:
        return iter(sorted(self.rules))


class Skipable(RuleUnit, ABC):
    is_skipable: bool = True

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


class Branch(RuleUnit[Rule]):
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
        return not self.is_terminal

    @property
    def is_terminal(self) -> bool:
        return isinstance(self.rule, Empty)

    @property
    def is_valid(self) -> bool:
        return self.rule == VALID

    @property
    def is_error(self) -> bool:
        return self.rule == ERROR

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for first, after in self.rule.splited:
            yield first, self.new_rule(after)

        if self.rule.is_skipable:
            yield Match(group=Group.always(), action=EXCLUDE), self.new_rule(VALID)


class BranchSet(RuleSet[Branch]):
    @classmethod
    def join(cls, args: Iterable[Branch]):
        return cls.make(*args)

    @classmethod
    def _flat(cls, *args: Branch) -> Iterable[Branch]:
        for arg in args:
            if isinstance(arg, cls):
                yield from cls._flat(*arg.rules)
            else:
                yield arg

    @classmethod
    def make(cls, *args: Branch) -> Union[Branch, BranchSet]:
        rules: List[Branch] = []

        for arg in cls._flat(*args):
            if arg not in rules:
                rules.append(arg)

        if len(rules) == 0:
            raise Exception("You need at least 1 branch into a branchset")

        if len(rules) == 1:
            return rules[0]

        return cls(*rules)

    def __init__(self, *rules: Branch):
        assert all(isinstance(rule, Branch) for rule in rules), list(map(type, rules))
        super().__init__(*rules)

    def __str__(self):
        return "\n".join(map(str, self.rules))

    @property
    def splited(self) -> Iterator[Tuple[Match, Branch]]:
        for branch in self.rules:
            for match, after in branch.splited:
                yield match, after

    @property
    def is_skipable(self) -> bool:
        return all(rule.is_skipable for rule in self)

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


class All(RuleList[Rule]):
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
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for rule_first, rule_after in self.decompose:
            for first, after in rule_first.splited:
                yield first, after & rule_after

    def __str__(self):
        return " & ".join(map(str, self))


class Any(RuleSet[Rule]):
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
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for rule in self:
            for first, after in rule.splited:
                yield first, after


class Match(RuleLeaf):
    is_skipable: bool = False

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


class Empty(RuleLeaf):
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

    @property
    def is_valid(self) -> bool:
        return self.valid

    @property
    def is_error(self) -> bool:
        return not self.valid

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        yield Match(group=Group(inverted=self.valid), action=EXCLUDE), self


RuleCast = Union[Rule, Item, Group, bool, frozenset, set, tuple, list]

VALID = Empty(True)
ERROR = Empty(False)
