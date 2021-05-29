from graph37 import DAG

from .constants import NT_STATE, T_STATE, ACTION, INCLUDE, EXCLUDE
from .rules import Group

__all__ = ["BuilderGraph"]


class STYLES:
    class NODES:
        class STATES:
            NON_TERMINAL = dict(shape="box", style="filled", fillcolor="white", color="blue")
            TERMINAL_VALID = dict(shape="box", style="filled", fillcolor="lime", color="blue")
            TERMINAL_ERROR = dict(shape="box", style="filled", fillcolor="red", color="blue")

        ACTION = dict(shape="box", style="filled", fillcolor="gray", color="blue")
        GROUP = dict(shape="box", style="filled", fillcolor="gold", color="blue")

        GROUP_ACTION = dict(shape="record", style="filled", fillcolor="#12fcd5", color="blue")
        GROUP_ACTION_INC = dict(shape="record", style="filled", fillcolor="#f9fc12", color="blue")
        GROUP_ACTION_EXC = dict(shape="record", style="filled", fillcolor="#abad0e", color="blue")

    class LINKS:
        BASE = dict(constraint="true", arrowhead="vee", arrowtail="none", color="white")


class BuilderGraph(DAG):
    @classmethod
    def encode(cls, text: str):
        letters = "abcdefghijklmnopqrstuvwxyz"
        for i in range(1, len(letters) - 1):
            text = text.replace(letters[:i] + letters[i + 1:], f"a-{letters[i]}{letters[i + 1]}-z")
        LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i in range(1, len(LETTERS) - 1):
            text = text.replace(LETTERS[:i] + LETTERS[i + 1:], f"A-{LETTERS[i]}{LETTERS[i + 1]}-Z")

        return text.replace(INCLUDE, 'INC') \
            .replace(EXCLUDE, 'EXC') \
            .replace("ABCDEFGHIJKLMNOPQRSTUVWXYZ", r"A-Z") \
            .replace("abcdefghijklmnopqrstuvwxyz", r"a-z") \
            .replace("ABCDEFGHIJKLMNOPQRSTUVWXY", r"A-Y") \
            .replace("abcdefghijklmnopqrstuvwxy", r"a-y") \
            .replace("BCDEFGHIJKLMNOPQRSTUVWXYZ", r"B-Z") \
            .replace("bcdefghijklmnopqrstuvwxyz", r"b-z") \
            .replace("0123456789", r"0-9")

    def non_terminal_state(self, value: NT_STATE):
        return self.node(
            type="non_terminal_state",
            label=str(value),
            style=STYLES.NODES.STATES.NON_TERMINAL
        )

    def terminal_error_state(self, value: T_STATE):
        return self.node(
            type="terminal_error_state",
            label='\n'.join(map(repr, sorted(self.encode(value)[1:].split('|')))),
            style=STYLES.NODES.STATES.TERMINAL_ERROR
        )

    def terminal_valid_state(self, value: T_STATE):
        return self.node(
            type="terminal_valid_state",
            label='\n'.join(map(repr, sorted(self.encode(value).split('|')))),
            style=STYLES.NODES.STATES.TERMINAL_VALID
        )

    def action(self, action: ACTION):
        return self.node(
            type="action",
            label=self.encode(action),
            style=STYLES.NODES.ACTION
        )

    def group(self, group: Group):
        return self.node(
            type="group",
            label=self.encode(str(group)),
            style=STYLES.NODES.GROUP
        )

    def link(self, origin, target, **config):
        return super().link(origin, target, style=STYLES.LINKS.BASE, **config)

    def group_action(self, group: Group, action: ACTION):
        gs = '{' + str(group) \
            .replace('|', r'\|') \
            .replace('\n', '|') \
            .replace('>', r'\>') \
            .replace('<', r'\<') \
            .replace('}', r'\}') \
            .replace('{', r'\{') + '}'
        return self.node(
            label=self.encode(f"{gs}|{action!s}"),
            style={
                INCLUDE: STYLES.NODES.GROUP_ACTION_INC,
                EXCLUDE: STYLES.NODES.GROUP_ACTION_EXC
            }.get(action, STYLES.NODES.GROUP_ACTION)
        )

    def chain(self, *elements):
        return [
            self.link(origin, target)
            for origin, target in zip(elements, elements[1:])
        ]

    def display(self, splines="ortho", ranksep=0.5, view: bool = True, fp: str = ""):
        import graphviz as gv

        import os
        os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz-2.38/bin/'

        dot = gv.Digraph(
            format="svg",
            engine="dot",
            graph_attr=dict(
                rankdir='TB',
                ranksep=str(ranksep),
                color='white',
                splines='ortho',
                bgcolor='black',
            )
        )

        for node in self.nodes:
            dot.node(
                name=str(id(node)),
                label=node.get("label", ""),
                **node.get("style", {})
            )

        for link in self.links:
            dot.edge(
                tail_name=str(id(link.origin)),
                head_name=str(id(link.target)),
                **link.get("style", {})
            )
        directory, filename = os.path.split(fp or self.get("name", "digraph"))
        if view:
            dot.view(filename=filename)
        else:
            directory, filename = os.path.split(fp or self.get("name", "digraph"))
            dot.render(cleanup=True, filename=filename, directory=directory, quiet=True)
