from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Callable, Iterator, Tuple, Optional, Type, Union, Iterable, FrozenSet, Hashable

from graph37 import Node
from python_generator import *

from .BuilderGraph import BuilderGraph
# from .ParserConfig import ParserConfig
from .constants import ACTION, STATE, NT_STATE, T_STATE
from .items import Group, Item
from .rules import BranchSet, Branch
from .utils import ArgsHashed

DEBUG_GROUP_TO_OUTCOME = False

__all__ = ["Optimizer"]


class AmbiguityException(Exception):
    pass


class ActionToBranch(ArgsHashed):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.action, self.branch

    def __init__(self, action: ACTION, branch: Branch):
        self.action: ACTION = action
        self.branch: Branch = branch

    @property
    def as_group(self) -> Outcome:
        return Outcome({self})


class Outcome(ArgsHashed):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), tuple(sorted(self.atbs))

    @classmethod
    def make(cls, outcomes: Iterable[Union[Outcome]]) -> Outcome:
        return cls([atb for outcome in outcomes for atb in outcome.atbs])

    def __init__(self, atbs: Iterable[ActionToBranch] = None):
        self.atbs: FrozenSet[ActionToBranch] = frozenset() if atbs is None else frozenset(atbs)

    @property
    def action_select(self) -> ActionSelect:
        action_select: ActionSelect = ActionSelect()
        for atb in self.atbs:
            action_select.add(atb.action, atb.branch)
        return action_select


class GroupToOutcome(Dict[Group, Outcome]):
    @classmethod
    def from_branch_set(cls, branch_set: BranchSet) -> GroupToOutcome:
        self: GroupToOutcome = cls()
        data = []
        for match, branch in branch_set.splited:
            data.append([str(branch), str(match.group), str(match.action), str(branch)])
            self.add(match.group, match.action, branch)

        if DEBUG_GROUP_TO_OUTCOME:
            from tools37 import ReprTable
            print(str(ReprTable(data)))

        return self

    def item_outcome(self, item: Optional[Item]) -> Outcome:
        if item is None:  # here None act as an unspecified item
            return Outcome.make(outcome for group, outcome in self.items() if group.inverted)
        else:
            return Outcome.make(outcome for group, outcome in self.items() if item in group)

    def alphabet(self, group_cls: Type[Group]) -> Group:
        return group_cls(item for group in self for item in group.items)

    def optimized(self, group_cls: Type[Group]) -> GroupToOutcome:
        alphabet: group_cls = self.alphabet(group_cls)

        default: Outcome = self.item_outcome(None)
        reverted = {default: ~alphabet}

        for item in alphabet.items:
            outcome: Outcome = self.item_outcome(item)
            if outcome in reverted:
                reverted[outcome] += item
            else:
                reverted[outcome] = group_cls({item})

        result = GroupToOutcome({isk: isv for isv, isk in reverted.items()})

        return result

    def add(self, group: Group, action: ACTION, branch: Branch) -> None:
        atb = ActionToBranch(action, branch)
        if group in self:
            self[group] = Outcome.make((self[group], Outcome({atb})))
        else:
            self[group] = Outcome({atb})


FUNC = Callable[[BranchSet], STATE]


class ERROR_MODE(Enum):
    FULL = "FULL"
    MOST = "MOST"
    NONE = "NONE"


@dataclass
class TargetSelect:
    nonte_branches: List[Branch] = field(default_factory=list)
    valid_branches: List[Branch] = field(default_factory=list)
    error_branches: List[Branch] = field(default_factory=list)
    valid_priority: int = 0
    error_priority: int = 0

    @property
    def target(self) -> BranchSet:
        return BranchSet.make(*self.nonte_branches, *self.valid_branches, *self.error_branches)

    @property
    def priority(self):
        if self.nonte_branches:
            return 2, 1
        elif self.valid_branches:
            return 1, self.valid_priority
        else:
            return 0, self.error_priority

    def add_branch(self, branch: Branch) -> None:
        if not branch.is_terminal:
            self.nonte_branches.append(branch)
        elif branch.is_valid:
            self.valid_priority = max(self.valid_priority, branch.priority)
            self.valid_branches.append(branch)
        elif branch.is_error:
            self.error_priority = max(self.error_priority, branch.priority)
            self.error_branches.append(branch)
        else:
            raise Exception(f"Unknown case for branch neither non-terminal, valid or error !")

    def get_target_states(self, func: FUNC) -> Iterator[STATE]:
        if self.nonte_branches:
            return [func(self.target)]
        elif self.valid_branches:
            return [T_STATE(branch.name) for branch in self.valid_branches]
        elif self.error_branches:
            return [T_STATE("!" + "|".join(sorted(branch.name for branch in self.error_branches)))]
        else:
            return [T_STATE("!")]

    def _data_valid(self, strict_propagator: bool) -> List[T_STATE]:
        valid_branches = [branch for branch in self.valid_branches if branch.priority == self.valid_priority]
        if not strict_propagator:
            return [T_STATE(valid_branch.name) for valid_branch in valid_branches]

        if len(valid_branches) == 1:
            return [T_STATE(valid_branches[0].name)]
        else:
            if valid_branches:
                raise AmbiguityException("\ntoo many :\n" + "\n".join(f"-> {b!r}" for b in valid_branches))
            else:
                if len(self.valid_branches) == 1:
                    return [T_STATE(self.valid_branches[0].name)]
                raise AmbiguityException("\nall null :\n" + "\n".join(f"-> {b!r}" for b in self.valid_branches))

    def _data_error(self, error_mode: ERROR_MODE) -> T_STATE:
        if error_mode == ERROR_MODE.FULL:
            error_branches = self.error_branches
        elif error_mode == ERROR_MODE.MOST:
            error_branches = [branch for branch in self.error_branches if branch.priority == self.error_priority]
        elif error_mode == ERROR_MODE.NONE:
            error_branches = []
        else:
            raise ValueError(error_mode, "invalid error mode")
        return T_STATE("!" + "|".join(sorted(branch.name for branch in error_branches)))

    def data(self, func: FUNC, strict_propagator: bool, error_mode: ERROR_MODE = ERROR_MODE.MOST) -> List[STATE]:
        if self.nonte_branches:
            return [func(self.target)]
        elif self.valid_branches:
            return self._data_valid(strict_propagator)
        elif self.error_branches:
            return [self._data_error(error_mode)]
        else:
            return [T_STATE("!")]


class ActionSelect(Dict[ACTION, TargetSelect]):
    def add(self, action: ACTION, branch: Branch) -> None:
        if action in self:
            target_select = self[action]
        else:
            self[action] = target_select = TargetSelect()
        target_select.add_branch(branch)

    @property
    def targets(self) -> Iterator[BranchSet]:
        """Return all the non-terminal branch-sets"""
        for target_select in self.values():
            if target_select.nonte_branches:
                yield target_select.target

    def data(self, func: FUNC, strict_propagator: bool = False) -> ActionSelectData:
        max_priority = max(target_select.priority for target_select in self.values())
        cases = {
            action: target_select.data(func, strict_propagator)
            for action, target_select in self.items()
            if target_select.priority == max_priority
        }

        if strict_propagator and len(cases) != 1:
            raise AmbiguityException(cases)

        return ActionSelectData(cases=cases)


class GroupSelect(Dict[Group, ActionSelect]):
    @staticmethod
    def from_gto(gto: GroupToOutcome) -> GroupSelect:
        return GroupSelect({
            group: outcome.action_select
            for group, outcome in gto.items()
        })

    @property
    def targets(self) -> Iterator[BranchSet]:
        for action_select in self.values():
            yield from action_select.targets

    def data(self, func: FUNC, strict_propagator: bool = False) -> GroupSelectData:
        *cases, default = sorted(self.items())

        return GroupSelectData(
            {
                group: action_select.data(func, strict_propagator)
                for group, action_select
                in cases
            },
            default[1].data(func, strict_propagator)
        )


class OriginSelect(Dict[BranchSet, GroupSelect]):
    def data(self, func: FUNC, strict_propagator: bool = False) -> OriginSelectData:
        return OriginSelectData(
            {
                func(origin): group_select.data(func, strict_propagator)
                for origin, group_select in self.items()
            }
        )


class Optimizer:
    def __init__(self, branch_set: BranchSet, group_cls: Type[Group]):
        self.branch_set: BranchSet = branch_set
        self.group_cls: Type[Group] = group_cls

        self.branch_sets: List[BranchSet] = [self.branch_set]
        self.origin_select: OriginSelect = OriginSelect()

        self.build()

    def build(self) -> None:
        """
            This will iteratively build the cases of the parser
            from the original branchset to all the possible consequent branchsets
        """
        index = 0
        while index < len(self.branch_sets):
            branch_set: BranchSet = self.branch_sets[index]
            index += 1

            group_select: GroupSelect = self.extract(branch_set)
            self.origin_select[branch_set] = group_select
            self.include(group_select)

        self.branch_sets = [self.branch_sets[0], *sorted(self.branch_sets[1:])]  # insure stable indexes

    def include(self, group_select: GroupSelect) -> None:
        for branch_set in group_select.targets:
            if branch_set.is_terminal:
                continue

            if branch_set in self.branch_sets:
                continue

            self.branch_sets.append(branch_set)

    def extract(self, branch_set: BranchSet) -> GroupSelect:
        gto: GroupToOutcome = GroupToOutcome.from_branch_set(branch_set).optimized(self.group_cls)
        group_select: GroupSelect = GroupSelect.from_gto(gto)
        return group_select

    def get_nt_state(self, branch_set: BranchSet) -> NT_STATE:
        return NT_STATE(self.branch_sets.index(branch_set))

    def data(self, strict_propagator: bool) -> OriginSelectData:
        return self.origin_select.data(self.get_nt_state, strict_propagator)


########################################################################################################################
# DATA TO CODE
########################################################################################################################


class ActionSelectData:
    def __init__(self, cases: Dict[ACTION, List[STATE]]):
        self.cases: Dict[ACTION, List[STATE]] = cases

    def code(self, _item: VAR, formal: bool) -> BLOCK:
        rtype = RETURN if formal else YIELD

        return BLOCK(*[
            rtype(ARGS(STR(action), INT(value) if isinstance(value, int) else STR(value)))
            for action, values in self.cases.items()
            for value in values
        ])


class GroupSelectData:
    def __init__(self, cases: Dict[Group, ActionSelectData], default: ActionSelectData):
        self.cases: Dict[Group, ActionSelectData] = cases
        self.default: ActionSelectData = default

    def code(self, item: VAR, formal: bool) -> Union[IF, BLOCK]:
        return SWITCH(
            cases=[(group.condition(item), asd.code(item, formal)) for group, asd in sorted(self.cases.items())],
            default=self.default.code(item, formal)
        )


class OriginSelectData:
    def __init__(self, cases: Dict[NT_STATE, GroupSelectData]):
        self.cases: Dict[NT_STATE, GroupSelectData] = cases

    def code(self, current: VAR, item: VAR, formal: bool) -> SWITCH:
        return SWITCH(
            cases=[(current.GETATTR("value").EQ(INT(value)), gsd.code(item, formal)) for value, gsd in
                   sorted(self.cases.items())],
            default=EXCEPTION(FSTR(f"value = {{{current.name}.value!r}}")).RAISE()
        )

#
# class ParserData:
#     def __init__(self, name: str, osd: OriginSelectData, config: ParserConfig):
#         self.name: str = name
#         self.osd: OriginSelectData = osd
#         self.config: ParserConfig = config
#
#     def build_propagator(self, imports: List[IMPORT.FROM]) -> DEF:
#         if self.config.strict_propagator:
#             t = "Tuple[ACTION, STATE]"
#             imports.append(IMPORT.FROM("item_engine", ["ACTION", "STATE"]))
#             imports.append(IMPORT.FROM("typing", "Tuple"))
#         else:
#             t = "Iterator[Tuple[ACTION, STATE]]"
#             imports.append(IMPORT.FROM("item_engine", ["ACTION", "STATE"]))
#             imports.append(IMPORT.FROM("typing", ["Tuple", "Iterator"]))
#
#         cur = VAR("cur")
#         old = VAR("old")
#
#         imports.append(IMPORT.TYPE(self.config.input_cls))
#         imports.append(IMPORT.TYPE(self.config.output_cls))
#
#         return DEF(
#             name=self.config.name + '_propagator',
#             args=ARGS(
#                 cur.ARG(t=self.config.output_cls.__name__),
#                 old.ARG(t=self.config.input_cls.__name__)
#             ),
#             block=self.osd.code(cur, old, self.config.strict_propagator),
#             t=t
#         )
#
#     def code(self) -> MODULE:
#         imports = []
#         propagator = self.build_propagator(imports)
#         function, module = self.config.build(propagator, imports)
#         return module
#
#     @property
#     def graph(self, **config):
#         dag = BuilderGraph(**config, name=self.name)
#
#         branch_set_nodes: Dict[STATE, Node] = {}
#         errors: Dict[T_STATE, Node] = {}
#         valids: Dict[T_STATE, Node] = {}
#
#         def getnode(value: STATE):
#             if isinstance(value, T_STATE):
#                 if value.startswith('!'):
#                     if value not in errors:
#                         errors[value] = dag.terminal_error_state(value)
#                     return errors[value]
#                 else:
#                     if value not in valids:
#                         valids[value] = dag.terminal_valid_state(value)
#                     return valids[value]
#             else:
#                 if value not in branch_set_nodes:
#                     branch_set_nodes[value] = dag.non_terminal_state(value)
#                 return branch_set_nodes[value]
#
#         memory = {}
#
#         def make_chain(o: NT_STATE, g: Group, a: ACTION, t: STATE):
#             origin_node = getnode(o)
#             target_node = getnode(t)
#             k1 = (g, a, target_node)
#             if k1 in memory:
#                 group_action_node = memory[k1]
#             else:
#                 memory[k1] = group_action_node = dag.group_action(g, a)
#                 dag.link(group_action_node, target_node)
#
#             k3 = (origin_node, group_action_node)
#             if k3 not in memory:
#                 memory[k3] = dag.link(origin_node, group_action_node)
#
#         for origin, gsd in self.osd.cases.items():
#             for group, asd in gsd.cases.items():
#                 for action, target in asd.cases.items():
#                     make_chain(origin, group, action, target)
#
#             for action, target in gsd.default.cases.items():
#                 make_chain(origin, Group.never(), action, target)
#
#         return dag
