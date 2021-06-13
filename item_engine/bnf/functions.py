import os
import shutil

LANG = 'bnf'
TARGET = os.path.abspath(os.path.join(__file__, os.pardir, 'grammar'))


def load(major: int, minor: int, patch: int):

    shutil.copyfile(src=f'build_{major}_{minor}_{patch}.py', dst='build.py')

    if os.path.exists(TARGET):
        shutil.rmtree(path=TARGET)
    print(f"successfully removed {os.path.relpath(TARGET, os.curdir)}")

    from item_engine.bnf.grammars import get_version_name, load_version

    load_version(lang=LANG, dst=TARGET, major=major, minor=minor, patch=patch)

    print(f"successfully loaded {get_version_name(LANG, major, minor, patch)}")


def reload_latest_version():
    if os.path.exists(TARGET):
        shutil.rmtree(path=TARGET)
    print(f"successfully removed {os.path.relpath(TARGET, os.curdir)}")

    load_latest_version()


def load_latest_version():
    from item_engine.bnf.grammars import load_latest_version, get_version_name
    latest_version = load_latest_version(lang=LANG, dst=TARGET)

    print(f"successfully loaded {get_version_name(LANG, *latest_version)}")
