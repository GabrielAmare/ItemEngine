import os
import re
import sys
from typing import Tuple

from item_engine import Branch, INF
from item_engine.bnf import SYMBOL_TABLE
from item_engine.bnf.functions import load
from item_engine.bnf.grammar import bnf as src2cst
from item_engine.bnf.grammar.materials import build as ast2cst, Grammar
from item_engine.textbase import alpha, alphanum, sq, n_sq, dq, n_dq

VERSION_REGEX = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")


def parse_version(value: str) -> Tuple[int, int, int]:
    match = VERSION_REGEX.match(value)
    if match:
        return int(match['major']), int(match['minor']), int(match['patch'])
    else:
        raise ValueError(value)


def reload(text: str = ''):
    if not text:
        text = input("Which version do you want to load ?\n  - 'latest'\n  - '<major>.<minor>.<patch>'\n>>> ")

    if not text:
        return False

    try:
        version = parse_version(text)
    except ValueError:
        print(f"invalid version specified : {repr(text)}")
        return False

    load(*version)
    return True


def build_grammar(src: str) -> Grammar:
    return ast2cst(src2cst(src))


def debug_grammar(src: str):
    import item_engine.bnf.grammar as gr

    chars = list(gr.bnf_characters(src))
    tokens = list(gr.tokenizer(chars))
    lemmas = list(gr.lemmatizer(tokens))

    from item_engine.textbase import rt_tokens, rt_lemmas

    print(rt_tokens(tokens))
    print(rt_lemmas(lemmas))


def generate_version(src: str, name: str, dst: str):
    with open(src, mode='r', encoding='utf-8') as file:
        content = file.read()

    try:
        grammar = build_grammar(content)
        print('successfully generated the new grammar')
    except Exception as e:
        debug_grammar(content)
        print('failed to generate the new grammar')
        print('reason :', e)
        return

    from item_engine.bnf.build import EngineBuilder

    builder = EngineBuilder(
        engine_name=name,
        whitespace=' \t\n',
        type_aliases={
            "VAR": str,
            "STR": str,
        },
        symbol_table=SYMBOL_TABLE
    )

    engine = builder.generate_engine(
        grammar=grammar,
        patterns=[
            Branch(
                name="VAR",
                rule=alpha & alphanum.repeat(0, INF),
                priority=50
            ),
            Branch(
                name="STR",
                rule=sq & n_sq.repeat(0, INF) & sq | dq & n_dq.repeat(0, INF) & dq,
                priority=50
            )
        ]
    )

    package = engine.package
    package.name = os.path.basename(dst)

    if os.path.exists(dst):
        allow_overwrite = input(f"Do you allow overwriting of {dst!r} ? (Y/N)\n>>> ") == 'Y'
    else:
        allow_overwrite = False

    package.save(root=os.path.dirname(dst), allow_overwrite=allow_overwrite)
    print(f"successfully built {dst!r}")


def generate(text: str):
    if not text:
        text = input('which version do you want to generate ?\n>>> ')

    major, minor, patch = parse_version(text)

    src = f"bnf_{major}_{minor}_{patch}.bnf"
    dst = f"grammars/bnf_{major}_{minor}_{patch}"

    generate_version(src=src, name='bnf', dst=dst)


def run_interpreter(text: str = ''):
    from item_engine.bnf.interpreter.main import main as run

    match = VERSION_REGEX.match(text)
    if match:
        text = f"bnf_{match['major']}_{match['minor']}_{match['patch']}.bnf"

    run(input_file=text)


COMMANDS = {
    'load': reload,
    'build': generate,
    'run': run_interpreter
}


class InvalidCommandError(Exception):
    pass


def parse_command(text: str):
    for alias, command in COMMANDS.items():
        if text.startswith(alias):
            return command(text[len(alias):].lstrip())
    else:
        raise InvalidCommandError


def main():
    while True:
        text = input("what do you want to do ?\n>>> ")

        if not text:
            sys.exit()

        try:
            parse_command(text)
        except InvalidCommandError:
            print('invalid command !')


if __name__ == '__main__':
    main()
