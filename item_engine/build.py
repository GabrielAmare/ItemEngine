from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Callable, Iterator, Tuple, Optional, Type, Union, Iterable, FrozenSet, Hashable

from python_generator import VAR, DEF, ARGS, INT, IF, BLOCK, STR, LIST, IMPORT, \
    RETURN, YIELD, SWITCH, FSTR, EXCEPTION, MODULE, PACKAGE, STATEMENT, ARG

# from .generic_items import GenericItem, GenericItemSet
from .constants import ACTION, STATE, NT_STATE, T_STATE
from .base import Group, BranchSet, Branch, Element, ArgsHashed, Item

from tools37 import CsvFile
from graph37 import Node
from .BuilderGraph import BuilderGraph

DEBUG_GROUP_TO_OUTCOME = False

__all__ = ["Parser", "Engine"]


class AmbiguityException(Exception):
    pass


class ActionToBranch:
    def __init__(self, action: ACTION, branch: Branch):
        self.action: ACTION = action
        self.branch: Branch = branch

    @property
    def as_group(self) -> Outcome:
        return Outcome({self})


class Outcome(ArgsHashed):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.atbs

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
        for branch in branch_set.branches:
            for first, after in branch.splited:
                data.append([str(branch), str(first.group), str(first.action), str(after)])
                self.add(first.group, first.action, branch.new_rule(after))

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
    non_terminal_part: BranchSet = field(default_factory=BranchSet)
    valid_branches: List[Branch] = field(default_factory=list)
    error_branches: List[Branch] = field(default_factory=list)
    valid_priority: int = 0
    error_priority: int = 0

    @property
    def target(self) -> BranchSet:
        return BranchSet({*self.non_terminal_part.branches, *self.valid_branches, *self.error_branches})

    @property
    def priority(self):
        if self.non_terminal_part:
            return 2, 1
        elif self.valid_branches:
            return 1, self.valid_priority
        else:
            return 0, self.error_priority

    def add_branch(self, branch: Branch) -> None:
        if not branch.is_terminal:
            self.non_terminal_part = BranchSet({*self.non_terminal_part.branches, branch})
        elif branch.is_valid:
            self.valid_priority = max(self.valid_priority, branch.priority)
            self.valid_branches.append(branch)
        elif branch.is_error:
            self.error_priority = max(self.error_priority, branch.priority)
            self.error_branches.append(branch)
        else:
            raise Exception(f"Unknown case for branch neither non-terminal, valid or error !")

    def get_target_states(self, func: FUNC) -> Iterator[STATE]:
        if self.non_terminal_part:
            return [func(self.target)]
        elif self.valid_branches:
            return [T_STATE(branch.name) for branch in self.valid_branches]
        elif self.error_branches:
            return [T_STATE("!" + "|".join(sorted(branch.name for branch in self.error_branches)))]
        else:
            return [T_STATE("!")]

    def _data_valid(self) -> T_STATE:
        valid_branches = [branch for branch in self.valid_branches if branch.priority == self.valid_priority]
        if len(valid_branches) == 1:
            return T_STATE(valid_branches[0].name)
        else:
            if valid_branches:
                raise AmbiguityException("\ntoo many :\n" + "\n".join(f"-> {b!r}" for b in valid_branches))
            else:
                if len(self.valid_branches) == 1:
                    return T_STATE(self.valid_branches[0].name)
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

    def data(self, func: FUNC, error_mode: ERROR_MODE = ERROR_MODE.MOST) -> STATE:
        if self.non_terminal_part:
            return func(self.target)
        elif self.valid_branches:
            return self._data_valid()
        elif self.error_branches:
            return self._data_error(error_mode)
        else:
            return T_STATE("!")


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
            if target_select.non_terminal_part:
                yield target_select.target

    def data(self, func: FUNC, formal: bool = False) -> ActionSelectData:
        max_priority = max(target_select.priority for target_select in self.values())
        cases = {
            action: target_select.data(func)
            for action, target_select in self.items()
            if target_select.priority == max_priority
        }

        if formal and len(cases) != 1:
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

    def data(self, func: FUNC, formal: bool = False) -> GroupSelectData:
        *cases, default = sorted(self.items())

        return GroupSelectData(
            {
                group: action_select.data(func, formal)
                for group, action_select
                in cases
            },
            default[1].data(func, formal)
        )


class OriginSelect(Dict[BranchSet, GroupSelect]):
    def data(self, func: FUNC, formal: bool = False) -> OriginSelectData:
        return OriginSelectData(
            {
                func(origin): group_select.data(func, formal)
                for origin, group_select in self.items()
            }
        )


class Parser:
    def __init__(self,
                 name: str,
                 branch_set: BranchSet,
                 input_cls: Type[Element],
                 output_cls: Type[Element],
                 group_cls: Type[Group],
                 skips: List[T_STATE],
                 reflexive: bool,
                 formal_inputs: bool,
                 formal_outputs: bool
                 ):
        """

        :param name: The name of the parser, it will be used to name the module
        :param branch_set: The BranchSet including all the patterns defined in the parser grammar
        :param input_cls: The type of elements the parser will receive
        :param output_cls: The type of elements the parser will emit
        :param skips: The list of element types that must be ignored (commonly used for white space patterns)
        :param reflexive: Will the parser receive what it emits (used to build recursive grammar)
        :param formal_inputs: Restrict the inputs to be consecutive
        :param formal_outputs: Is the parser formal ? If it's the case, any ambiguity will raise a SyntaxError
        """
        self.name: str = name
        self.branch_set: BranchSet = branch_set
        self.input_cls: Type[Element] = input_cls
        self.output_cls: Type[Element] = output_cls
        self.group_cls: Type[Group] = group_cls
        self.reflexive: bool = reflexive
        self.formal_inputs: bool = formal_inputs
        self.formal_outputs: bool = formal_outputs
        self.skips: List[T_STATE] = skips

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

    def data(self) -> ParserData:
        return ParserData(
            name=self.name,
            input_cls=self.input_cls,
            output_cls=self.output_cls,
            formal_inputs=self.formal_inputs,
            formal_outputs=self.formal_outputs,
            osd=self.origin_select.data(self.get_nt_state, self.formal_outputs),

            reflexive=self.reflexive,
            skips=self.skips
        )

    def to_csv(self, fp: str) -> None:
        data = []

        for origin, group_select in self.origin_select.items():
            for group, action_select in (*group_select.cases, (Group.never(), group_select.default)):
                for action, target_select in action_select.items():
                    for target_state in target_select.get_target_states(self.get_nt_state):
                        data.append(dict(
                            origin=str(self.get_nt_state(origin)),
                            group=str(group).replace('\n', ''),
                            action=action,
                            target=target_state
                        ))

        CsvFile.save(fp, keys=["origin", "group", "action", "target"], data=data)

    @property
    def graph(self, **config):
        return self.data().graph


class Engine:
    def __init__(self,
                 name: str,
                 parsers: List[Parser],
                 operators: Optional[MODULE] = None
                 ):
        assert name.isidentifier()
        assert not any(parser.name == 'operators' for parser in parsers)
        self.name: str = name
        self.parsers: List[Parser] = parsers
        self.operators: Optional[MODULE] = operators

    def build(self, root: str = os.curdir, allow_overwrite: bool = False) -> None:
        self.data().code().save(root=root, allow_overwrite=allow_overwrite)

    def data(self) -> EngineData:
        return EngineData(
            self.name,
            *[parser.data() for parser in self.parsers],
            materials=self.operators
        )


########################################################################################################################
# DATA TO CODE
########################################################################################################################


class ActionSelectData:
    def __init__(self, cases: Dict[ACTION, STATE]):
        self.cases: Dict[ACTION, STATE] = cases

    def code(self, item: VAR, formal: bool) -> BLOCK:
        rtype = RETURN if formal else YIELD

        return BLOCK(*[
            rtype(ARGS(STR(action), INT(value) if isinstance(value, int) else STR(value)))
            for action, value in self.cases.items()
        ])


class GroupSelectData:
    def __init__(self, cases: Dict[Group, ActionSelectData], default: ActionSelectData):
        self.cases: Dict[Group, ActionSelectData] = cases
        self.default: ActionSelectData = default

    def code(self, item: VAR, formal: bool) -> Union[IF, BLOCK]:
        return SWITCH(
            cases=[(group.condition(item), asd.code(item, formal)) for group, asd in self.cases.items()],
            default=self.default.code(item, formal)
        )


class OriginSelectData:
    def __init__(self, cases: Dict[NT_STATE, GroupSelectData]):
        self.cases: Dict[NT_STATE, GroupSelectData] = cases

    def code(self, current: VAR, item: VAR, formal: bool) -> SWITCH:
        return SWITCH(
            cases=[(current.GETATTR("value").EQ(INT(value)), gsd.code(item, formal)) for value, gsd in
                   self.cases.items()],
            default=EXCEPTION(FSTR("value = {current.value!r}")).RAISE()
        )


class ParserData:
    def __init__(self,
                 name: str,
                 input_cls: Type[Element],
                 output_cls: Type[Element],
                 osd: OriginSelectData,
                 formal_inputs: bool,
                 formal_outputs: bool,

                 skips: List[str] = None,
                 reflexive: bool = False
                 ):
        self.name: str = name
        self.osd: OriginSelectData = osd
        self.input_cls: Type[Element] = input_cls
        self.output_cls: Type[Element] = output_cls
        self.formal_inputs: bool = formal_inputs
        self.formal_outputs: bool = formal_outputs

        self.skips: List[str] = skips or []
        self.reflexive: bool = reflexive

    def code(self) -> MODULE:
        current = VAR("current")
        item = VAR("item")

        rtype = "Tuple[ACTION, STATE]" if self.formal_outputs else "Iterator[Tuple[ACTION, STATE]]"

        from .builders import build_func

        return MODULE(
            self.name,
            [
                IMPORT.FROM("typing", "Tuple"),
                *([] if self.formal_outputs else [IMPORT.FROM("typing", "Iterator")]),
                IMPORT.FROM("item_engine", ["ACTION", "STATE"]),
                IMPORT.FROM(self.input_cls.__module__, self.input_cls.__name__),
                IMPORT.FROM(self.output_cls.__module__, self.output_cls.__name__),
                VAR("__all__").ASSIGN(LIST([STR(self.name)])),
                DEF(
                    name=f"_{self.name}",
                    args=ARGS(
                        current.ARG(t=self.output_cls.__name__),
                        item.ARG(t=self.input_cls.__name__)
                    ),
                    block=self.osd.code(current, item, self.formal_outputs),
                    t=rtype
                ),
                build_func(
                    name=self.name,
                    fun=f"_{self.name}",
                    formal_inputs=self.formal_inputs,
                    formal_outputs=self.formal_outputs,
                    reflexive=self.reflexive,
                    input_cls=self.input_cls,
                    output_cls=self.output_cls,
                    skips=self.skips
                )
            ])

    @property
    def graph(self, **config):
        dag = BuilderGraph(**config, name=self.name)

        branch_set_nodes: Dict[STATE, Node] = {}
        errors: Dict[T_STATE, Node] = {}
        valids: Dict[T_STATE, Node] = {}

        def getnode(value: STATE):
            if isinstance(value, T_STATE):
                if value.startswith('!'):
                    if value not in errors:
                        errors[value] = dag.terminal_error_state(value)
                    return errors[value]
                else:
                    if value not in valids:
                        valids[value] = dag.terminal_valid_state(value)
                    return valids[value]
            else:
                if value not in branch_set_nodes:
                    branch_set_nodes[value] = dag.non_terminal_state(value)
                return branch_set_nodes[value]

        memory = {}

        def make_chain(origin: NT_STATE, group: Group, action: ACTION, target: STATE):
            origin_node = getnode(origin)
            target_node = getnode(target)
            k1 = (group, action, target_node)
            if k1 in memory:
                group_action_node = memory[k1]
            else:
                memory[k1] = group_action_node = dag.group_action(group, action)
                dag.link(group_action_node, target_node)

            k3 = (origin_node, group_action_node)
            if k3 not in memory:
                memory[k3] = dag.link(origin_node, group_action_node)

        for origin, gsd in self.osd.cases.items():
            for group, asd in gsd.cases.items():
                for action, target in asd.cases.items():
                    make_chain(origin, group, action, target)

            for action, target in gsd.default.cases.items():
                make_chain(origin, Group.never(), action, target)

        return dag


class EngineData:
    def __init__(self, name: str, *pds: ParserData, materials: MODULE = None):
        self.name: str = name
        self.pds: Tuple[ParserData] = pds
        self.materials: Optional[MODULE] = materials

    def code(self) -> PACKAGE:
        imports: List[STATEMENT] = []
        for parser_data in self.pds:
            imports.append(IMPORT.FROM("." + parser_data.name, parser_data.name))

        fp = self.pds[0]
        lp = self.pds[-1]

        res = VAR("src")

        imports.append(IMPORT.FROM(fp.input_cls.__module__, fp.input_cls.__name__))
        imports.append(IMPORT.FROM(lp.output_cls.__module__, lp.output_cls.__name__))

        for pd in self.pds:
            res = VAR(pd.name).CALL(res)

        return PACKAGE(
            self.name,
            MODULE(
                '__init__',
                scope=[
                    *imports,
                    IMPORT.FROM("typing", "Iterator"),
                    IMPORT.FROM(".materials", "*"),
                    VAR("__all__").ASSIGN(LIST([STR("parse")])),
                    DEF(
                        name="parse",
                        args=ARG("src", t=f"Iterator[{fp.input_cls.__name__}]"),
                        t=f"Iterator[{lp.output_cls.__name__}]",
                        block=RETURN(res)
                    )
                ]),
            *([] if self.materials is None else [self.materials]),
            *[parser.code() for parser in self.pds]
        )
