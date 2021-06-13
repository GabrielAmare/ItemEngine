"""
    Shell entry point for the bnf package
"""
from __future__ import annotations

import importlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, astuple, asdict

from python_generator import PACKAGE

from item_engine.bnf_2.interpreter import App, TextStyle


@dataclass
class ShellConfig:
    fp: str = 'shell_config.json'
    origin: str = '_._._'
    target: str = '_._._'

    @classmethod
    def load(cls, fp: str):
        if not fp.endswith('.json'):
            fp += '.json'

        if os.path.exists(fp):
            with open(fp, mode='r', encoding='utf-8') as file:
                data = json.load(file)
        else:
            data = {}

        return cls(**data)

    def save(self):
        data = asdict(self)
        data.pop('fp')
        with open(self.fp, mode='w', encoding='utf-8') as file:
            json.dump(data, file)


@dataclass
class Version:
    __VERSION_STR_REGEX = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")
    __VERSION_DIR_REGEX = re.compile(r"^v_(?P<major>\d+)_(?P<minor>\d+)_(?P<patch>\d+)$")
    major: int
    minor: int
    patch: int

    @classmethod
    def from_str(cls, expr: str) -> Version:
        match = cls.__VERSION_STR_REGEX.match(expr)

        if not match:
            raise ValueError(expr)

        return cls(int(match['major']), int(match['minor']), int(match['patch']))

    @classmethod
    def from_dir(cls, expr: str) -> Version:
        match = cls.__VERSION_DIR_REGEX.match(expr)

        if not match:
            raise ValueError(expr)

        return cls(int(match['major']), int(match['minor']), int(match['patch']))

    def major_up(self) -> Version:
        return Version(self.major + 1, 0, 0)

    def minor_up(self) -> Version:
        return Version(self.major, self.minor + 1, 0)

    def patch_up(self) -> Version:
        return Version(self.major, self.minor, self.patch + 1)

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def directory(self) -> str:
        return f"v_{self.major}_{self.minor}_{self.patch}"

    def __lt__(self, other):
        if type(self) is type(other):
            return astuple(self) < astuple(other)
        else:
            return NotImplemented

    def exists(self, root: str = os.curdir) -> bool:
        return os.path.exists(os.path.join(root, self.directory()))


class VersionNotFoundError(FileNotFoundError):
    def __init__(self, version: Version):
        self.version: Version = version


class VersionExistsError(FileExistsError):
    def __init__(self, version: Version):
        self.version: Version = version


class InvalidCommandError(Exception):
    def __init__(self, command: str, reason: str = ''):
        self.command: str = command
        self.reason: str = reason

    def __str__(self):
        return f"Invalid Command Error :\n  - command = {self.command!r}\n  - reason = {self.reason}"


def shell_input(config: ShellConfig, msg: str = ''):
    if msg and not msg.endswith('\n'):
        msg += '\n'
    return input(f"{msg}[{config.origin}/{config.target}] >>> ")


def _check_version_exists(path, *args):
    if not os.path.exists(path):
        raise InvalidCommandError(*args)


def _check_version_not_exists(path, *args):
    if os.path.exists(path):
        raise InvalidCommandError(*args)


def _extract_version(expr, *args):
    try:
        return Version.from_str(expr)
    except ValueError:
        raise InvalidCommandError(*args)


def _get_all_versions():
    for name in os.listdir(os.curdir):
        try:
            yield Version.from_dir(name)
        except ValueError:
            pass


def _get_latest_version(*args):
    versions = list(_get_all_versions())
    if versions:
        return max(versions)
    else:
        raise InvalidCommandError(*args)


class VersionManager:
    def __init__(self, config: ShellConfig, logger=print):
        self.config = config
        self.logger = logger

    def _get_version(self, expr: str):
        try:
            return Version.from_str(expr)
        except ValueError:
            raise VersionNotFoundError(*args)

    def get_builder(self, version: Version, _is_root: bool = True):
        if not version.exists():
            raise VersionNotFoundError(version)

        builder = importlib.import_module(f"item_engine.bnf_2.{version.directory()}.builder")

        if _is_root:
            self.logger(f"v{version!s} builder successfully acquired")

        return builder

    def build_package(self, version_to_use: Version, version_to_build: Version, _is_root: bool = True) -> PACKAGE:
        builder = self.get_builder(version_to_use, _is_root=False)

        grammar_fp = os.path.join(version_to_build.directory(), "grammar.bnf")

        if not os.path.exists(grammar_fp):
            raise FileNotFoundError(grammar_fp)

        package = builder.generate(grammar_fp)

        if _is_root:
            self.logger(f"package {package.name} successfully built")

        return package

    def build(self, version_to_use: Version, version_to_build: Version, _is_root: bool = True):
        dst = version_to_build.directory()

        package = self.build_package(version_to_use, version_to_build, _is_root=False)

        package_path = f"{dst}/{package.name!s}"

        if os.path.exists(package_path):
            if shell_input(self.config, f"{package_path!r} already exists. Do you allow overwrite ? (Y/N)") != 'Y':
                return

        package.save(root=dst, allow_overwrite=True)

        if _is_root:
            self.logger(f"successfully built v{version_to_build!s} using v{version_to_use!s}")

    def auto_build(self, version: Version, _is_root: bool = True):
        self.build_package(version, version, _is_root=False)

        if _is_root:
            self.logger(f"v{version!s} successfully auto-built")

    def spec_build(self, version: Version, _is_root: bool = True):
        builder = self.get_builder(version, _is_root=False)

        grammar_fp = os.path.join(version.directory(), "grammar.bnf")

        if not hasattr(builder, 'build_grammar'):
            self.logger(f"v{version!s} unable to build __spec__.py (build_grammar function not defined)")
            return

        grammar = builder.build_grammar(grammar_fp)

        with open(f"{version.directory()}/__spec__.py", mode='w', encoding='utf-8') as file:
            file.write(f"from .engine import *\n\n{grammar!r}")

        if _is_root:
            self.logger(f"v{version!s} successfully built __spec__.py")

    def gui(self, version: Version, input_file: str = None):
        if not version.exists():
            raise VersionNotFoundError(version)

        dst = version.directory()

        engine = importlib.import_module(f"item_engine.bnf_2.{dst}.engine.__init__")

        style_fp = f"{dst}/style.json"
        if os.path.exists(style_fp):
            with open(style_fp, mode='r', encoding='utf-8') as file:
                style_data = json.load(file)
        else:
            style_data = {}

        style = TextStyle.from_dict(style_data)

        app = App(
            characters=engine.parse_characters,
            tokenizer=engine.tokenizer,
            lemmatizer=engine.lemmatizer,
            transpiler=None,
            style=style,
            input_file=input_file
        )
        app.mainloop()


class CommandParser:
    def __init__(self, manager: VersionManager, config: ShellConfig):
        self.manager: VersionManager = manager
        self.config: ShellConfig = config

        self.COMMANDS = {
            'exit': self.quit,
            'quit': self.quit,
            'create': self.create,
            'load': self.load,
            'patch': self.patch,
            'build': self.build,
            'autobuild': self.auto_build,
            'specbuild': self.spec_build,
            'gui': self.gui
        }

    def __call__(self, command: str):
        if command in self.COMMANDS:
            function = self.COMMANDS[command]
            return function('')

        for keyword, function in self.COMMANDS.items():
            if command.startswith(keyword + ' '):
                function, command = self.COMMANDS[keyword], command[len(keyword) + 1:]
                return function(command)

        raise InvalidCommandError(command, 'no command found')

    def quit(self, _: str):
        self.config.save()
        sys.exit(0)

    def create(self, command: str):
        new_version = _extract_version(command, command, "version argument invalid")

        dst = new_version.directory()

        _check_version_not_exists(dst, command, "version already exists")

        os.mkdir(dst)

        with open(f"{dst}/__init__.py", mode='w', encoding='utf-8') as file:
            file.write("from .build import *\n"
                       "from .grammar import *")

        with open(f"{dst}/__spec__.py", mode='w', encoding='utf-8') as file:
            pass
        with open(f"{dst}/build.py", mode='w', encoding='utf-8') as file:
            pass
        with open(f"{dst}/builder.py", mode='w', encoding='utf-8') as file:
            pass
        with open(f"{dst}/grammar.bnf", mode='w', encoding='utf-8') as file:
            pass
        with open(f"{dst}/style.json", mode='w', encoding='utf-8') as file:
            file.write("{\n"
                       "}")

        self.config.target = str(new_version)

    def patch(self, command: str):
        if command:
            source_version = _extract_version(command, command, "version argument invalid")
        else:
            source_version = _extract_version(self.config.origin, command, "no version specified, cannot apply patch")

        src = source_version.directory()

        _check_version_exists(src, command, f"source version {source_version!s} doesn't exist")

        patch_version = source_version.patch_up()

        dst = patch_version.directory()

        _check_version_not_exists(dst, command, f"patch version {patch_version!s} already exist")

        os.mkdir(dst)

        shutil.copyfile(src=f"{src}/__init__.py", dst=f"{dst}/__init__.py")
        shutil.copyfile(src=f"{src}/build.py", dst=f"{dst}/build.py")
        shutil.copyfile(src=f"{src}/builder.py", dst=f"{dst}/builder.py")
        shutil.copyfile(src=f"{src}/grammar.bnf", dst=f"{dst}/grammar.bnf")
        shutil.copyfile(src=f"{src}/style.json", dst=f"{dst}/style.json")

        self.config.origin = str(source_version)
        self.config.target = str(patch_version)

    def load(self, command: str):
        if command:
            try:
                version = Version.from_str(command)
            except ValueError:
                raise InvalidCommandError(command, "invalid argument for version")
        else:
            try:
                version = Version.from_str(self.config.target)
                self.config.target = '_._._'
            except ValueError:
                version = _get_latest_version(command, "no version found")

        _check_version_exists(version.directory(), command, "version doesn't exists")

        self.config.origin = str(version)

    def build(self, command: str):
        version_to_use = _extract_version(self.config.origin, command, "version-to-use argument invalid")

        if command:
            version_to_build = _extract_version(command, command, "version-to-build argument invalid")
        else:
            version_to_build = _extract_version(self.config.target, command, "version-to-build argument invalid")

        self.manager.build(version_to_use, version_to_build)

        self.config.target = str(version_to_build)

    def auto_build(self, command: str):
        if command:
            version = _extract_version(command, command, "version-to-autobuild argument invalid")
        else:
            try:
                version = _extract_version(self.config.target, command, "version-to-autobuild argument invalid")
            except InvalidCommandError:
                version = _extract_version(self.config.origin, command, "version-to-autobuild argument invalid")

        self.manager.auto_build(version)

    def spec_build(self, command: str):
        if command:
            version = _extract_version(command, command, "version-to-specbuild argument invalid")
        else:
            try:
                version = _extract_version(self.config.target, command, "version-to-specbuild argument invalid")
            except InvalidCommandError:
                version = _extract_version(self.config.origin, command, "version-to-specbuild argument invalid")

        self.manager.spec_build(version)

    def gui(self, command: str):
        version_to_use = _extract_version(self.config.origin, command, "no specified version to run")

        try:
            version = _extract_version(command)
            input_file = f"{version.directory()}/grammar.bnf"
        except:
            if os.path.exists(command):
                input_file = command
            else:
                input_file = None

        self.manager.gui(version_to_use, input_file)


def read(command_parser: CommandParser, command: str):
    commands = list(map(str.strip, command.split('&')))

    for command in commands:
        try:
            command_parser(command)
        except InvalidCommandError as e:
            print(e)
            return


def loop(command_parser):
    while True:
        command = shell_input(command_parser.config)
        read(command_parser, command)


def main():
    config: ShellConfig = ShellConfig.load('shell_config.json')
    manager: VersionManager = VersionManager(config, logger=lambda *args, **kwargs: print('  -', *args, **kwargs))
    command_parser: CommandParser = CommandParser(manager, config)

    # read(command_parser, "load 0.0.2 & build 0.0.3")
    # read(command_parser, "load 0.0.3 & build 0.0.4")
    # read(command_parser, "autobuild 0.0.4")
    loop(command_parser)


if __name__ == '__main__':
    main()
