import os
import types

TARGET = 'testimport'


def module_version_1():
    with open(TARGET + '.py', mode='w', encoding='utf-8') as file:
        file.write("def function():\n\tprint('version 1')")


def module_version_2():
    with open(TARGET + '.py', mode='w', encoding='utf-8') as file:
        file.write("def function():\n\tprint('version 2')")


def load_module(name: str, root: str = os.curdir):
    fp = os.path.join(root, name + '.py')

    with open(fp, mode='r', encoding='utf-8') as file:
        code = file.read()

    module = types.ModuleType(name)

    exec(code, module.__dict__)

    return module


def main():
    module_version_1()

    module = load_module(TARGET)

    module.function()

    module_version_2()

    module = load_module(TARGET)

    module.function()


if __name__ == '__main__':
    main()
