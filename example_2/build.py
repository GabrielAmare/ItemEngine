import os
import time

from tools37 import Console

from item_engine.textbase.generate_tests import generate_tests

console = Console(show_times=False, show_count=False, show_debug=False)


def _build_engine():
    if not os.path.exists('spec.py'):
        console.warn("no specification file")
        raise FileNotFoundError('spec.py')

    try:
        from example_2.spec import engine
    except ImportError as e:
        console.error("no engine in 'spec.py'")
        time.sleep(0.1)
        raise e

    try:
        engine.build(root='.', allow_overwrite=True)
    except Exception as e:
        console.error(f"build error for engine in 'spec.py'")
        raise e

    console.log("engine built")


def _test_engine():
    if not os.path.exists('__test__.py'):
        console.warn("no tests file '__test__.py'")
        return

    try:
        from example_2.__test__ import run
    except ImportError as e:
        console.error("no run function in '__test__.py'")
        time.sleep(0.1)
        raise e
    try:
        run()
    except Exception as e:
        console.error(f"tests failure in '__test__.py'\n")
        time.sleep(0.1)
        raise e

    console.log("engine tested")


def _regen_tests():
    if not os.path.exists('tests.inputs'):
        console.warn("cannot generate tests : no 'tests.inputs' file")
        return

    with open('tests.inputs', mode='r', encoding='utf-8') as file:
        inputs = file.read().split('\n')

    if not inputs:
        console.print("cannot generate tests : no tests inputs to generate into 'tests.inputs'")
        return

    exists = os.path.exists('__test__.py')

    try:
        generate_tests(
            pckg='example_2',
            inputs=inputs,
            # remove_preview=False
        )
    except Exception as e:
        console.error(f"error while trying to generate tests from inputs !")
        time.sleep(0.1)
        raise e

    console.log(f"tests {'re' if exists else ''}generated")


def main():
    # build the engine
    _build_engine()

    # test the engine
    _test_engine()

    # regenerate tests
    _regen_tests()


if __name__ == '__main__':
    main()
