from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Tuple, Iterator, FrozenSet, List, TypeVar, Generic, Type, Union, Hashable
from functools import reduce
from operator import and_

from .constants import ACTION, INCLUDE, EXCLUDE, AS, IN, T_STATE, INDEX, STATE, CASE, NT_STATE, INF, EOF
from .generic_items import GenericItem, GenericItemSet
import python_generator as pg

__all__ = [
    "Rule", "RuleUnit", "RuleList", "Empty",  # abstracts
    "Optional", "Repeat", "All", "Any",  # composed
    "Match", "VALID", "ERROR"  # simple
]


class ArgsHashed(Hashable):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        raise NotImplementedError

    def __eq__(self, other: ArgsHashed):
        return self.__args__ == other.__args__

    def __hash__(self):
        return hash(self.__args__)

    def __lt__(self, other: ArgsHashed):
        return self.__args__ < other.__args__


########################################################################################################################
# Rule
########################################################################################################################

class Rule(ArgsHashed):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __and__(self, other: Rule) -> Rule:
        if isinstance(self, Empty):
            return other if self.valid else self

        if isinstance(other, Empty):
            return self if other.valid else other

        return All(*self.all, *other.all)

    def __or__(self, other) -> Rule:
        if isinstance(self, Empty):
            return other

        if isinstance(other, Empty):
            return self

        return Any(*self.any, *other.any)

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

    def repeat(self: Union[Repeat, Optional, All, Any, Match, Empty], mn: int = 0, mx: int = INF) -> Rule:
        assert mn >= 0
        assert mx == -1 or (mx >= mn and mx > 0)

        if mn == 0:
            base = Empty(valid=True)
        else:
            base = All(*(mn * self.all))

        if mx == INF:
            return base & Repeat(self)
        else:
            return base & All(*((mx - mn) * self.all))

    @property
    def optional(self: Union[Repeat, Optional, All, Any, Match, Empty]) -> Union[Repeat, Optional, Empty]:
        return Optional(self)

    @property
    def all(self) -> List[Rule]:
        return list(self.rules) if isinstance(self, All) else [self]

    @property
    def any(self) -> List[Rule]:
        return list(self.rules) if isinstance(self, Any) else [self]


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


class RuleUnit(Rule):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.rule

    def __init__(self, rule: Rule):
        self.rule: Rule = rule

    def __repr__(self):
        return f"{self.__class__.__name__}({self.rule!r})"

    def __str__(self):
        raise NotImplementedError

    @property
    def is_skipable(self) -> bool:
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

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return self.rule.alphabet


class RuleList(Rule):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return (type(self), *self.rules)

    def __init__(self, *rules: Rule):
        self.rules: List[Rule] = list(rules)

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(map(repr, self.rules))})"

    def __str__(self):
        raise NotImplementedError

    @property
    def is_skipable(self) -> bool:
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

    def __iter__(self) -> Iterator[Rule]:
        return iter(self.rules)

    def __len__(self) -> int:
        return len(self.rules)

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return frozenset({item for rule in self.rules for item in rule.alphabet})


########################################################################################################################
# Optional | Repeat | All | Any
########################################################################################################################

class Skipable(RuleUnit):
    is_skipable: bool = True
    is_non_terminal: bool = True
    is_terminal: bool = False
    is_valid: bool = False
    is_error: bool = False

    @classmethod
    def make(cls, rule: Rule) -> Union[Skipable, Empty]:
        if isinstance(rule, Repeat):
            return rule

        if isinstance(rule, Empty):
            return VALID

        if isinstance(rule, Optional):
            rule = rule.rule

        return cls(rule)

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


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
    def make(cls, *args: Rule):
        rules: List[Rule] = []

        for arg in args:
            if isinstance(arg, cls):
                rules.extend(arg.rules)
            else:
                rules.append(arg)

        if len(rules) == 1:
            return rules[0]

        return cls(*rules)

    def __init__(self, *rules: Rule):
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
        return all(rule.is_skipable for rule in self.rules)

    @property
    def is_non_terminal(self) -> bool:
        return len(self.rules) != 1 or self.rules[0].is_non_terminal

    @property
    def is_terminal(self) -> bool:
        return len(self.rules) == 1 and self.rules[0].is_terminal

    @property
    def is_valid(self) -> bool:
        return len(self.rules) == 1 and self.rules[0].is_valid

    @property
    def is_error(self) -> bool:
        return len(self.rules) == 1 and self.rules[0].is_error

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for rule_first, rule_after in self.decompose:
            for first, after in rule_first.splited:
                yield first, after & rule_after

    def __str__(self):
        return " & ".join(map(str, self.rules))


class Any(RuleList):
    @classmethod
    def make(cls, *args: Rule):
        rules: List[Rule] = []

        for arg in args:
            if isinstance(arg, cls):
                for rule in arg.rules:
                    if rule not in rules:
                        rules.append(rule)
            elif arg not in rules:
                rules.append(arg)

        if len(rules) == 1:
            return rules[0]

        return cls(*rules)

    def __init__(self, *rules: Rule):
        assert len(rules) > 1
        assert not any(isinstance(rule, Any) for rule in rules)
        assert not any(isinstance(rule, Empty) for rule in rules[:-1])
        super().__init__(*rules)

    def __str__(self):
        return " | ".join(map(str, self.rules))

    @property
    def is_skipable(self) -> bool:
        return any(rule.is_skipable for rule in self.rules)

    @property
    def is_non_terminal(self) -> bool:
        return any(rule.is_non_terminal for rule in self.rules)

    @property
    def is_terminal(self) -> bool:
        return all(rule.is_terminal for rule in self.rules)

    @property
    def is_valid(self) -> bool:
        return all(rule.is_valid for rule in self.rules)

    @property
    def is_error(self) -> bool:
        return all(rule.is_error for rule in self.rules)

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for rule in self.rules:
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


class ItemInterface:
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


@dataclass(frozen=True, order=True)
class Item(GenericItem, ItemInterface):
    @property
    def as_group(self) -> Group:
        raise NotImplementedError


E = TypeVar("E", bound=Item)


class Group(GenericItemSet[E], Generic[E], ItemInterface):
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

@dataclass(frozen=True, order=True)
class Branch(GenericItem):
    name: str
    rule: Rule
    priority: int = 0
    transfer: bool = False

    @property
    def as_group(self) -> BranchSet:
        return BranchSet(frozenset({self}))

    def new_rule(self, rule: Rule) -> Branch:
        return replace(self, rule=rule)

    def __str__(self):
        return f"{self.name!s}[{self.priority}] : {self.rule!s}"

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return self.rule.alphabet

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


class BranchSet(GenericItemSet[Branch]):
    def __bool__(self):
        return bool(self.items)

    def terminal_code(self, throw_errors: bool = False) -> Iterator[T_STATE]:
        valid_branches = [branch for branch in self.items if branch.is_valid]
        valid_max_priority = max([branch.priority for branch in valid_branches], default=0)
        valid_names = [T_STATE(branch.name) for branch in valid_branches if branch.priority == valid_max_priority]

        if valid_names:
            return valid_names

        error_branches = [branch for branch in self.items if branch.is_error]
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
        for branch in self.items:
            for first, after in branch.splited:
                yield first.group, first.action, branch.new_rule(after)

    @property
    def only_non_terminals(self) -> BranchSet:
        """Remove the terminal branches"""
        return BranchSet(frozenset(branch for branch in self.items if not branch.is_terminal))

    @property
    def only_valids(self) -> BranchSet:
        """Remove the terminal branches"""
        return BranchSet(frozenset(branch for branch in self.items if branch.is_valid))

    @property
    def only_errors(self) -> BranchSet:
        """Remove the terminal branches"""
        return BranchSet(frozenset(branch for branch in self.items if branch.is_error))

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
        return any(branch.is_non_terminal for branch in self.items)

    @property
    def is_terminal(self) -> bool:
        return all(branch.is_terminal for branch in self.items)

    @property
    def is_valid(self) -> bool:
        return all(branch.is_valid for branch in self.items)

    @property
    def is_error(self) -> bool:
        return all(branch.is_error for branch in self.items)

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return frozenset({item for branch in self.items for item in branch.alphabet})


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
