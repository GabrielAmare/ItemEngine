from item_engine.textbase import *
from item_engine.builders.MB1 import META_BUILDER_1
from item_engine.builders.MB3 import META_BUILDER_3
from item_engine.builders.MB4 import META_BUILDER_4
from item_engine.builders.MB5 import META_BUILDER_5
from python_generator import PACKAGE, MODULE


def main():
    package = PACKAGE(
        "package",
        MODULE("__init__"),
        MODULE("mb1", META_BUILDER_1(name="function", fun="_function", input_cls=Char, output_cls=Token)),
        MODULE("mb3", META_BUILDER_3(name="function", fun="_function", input_cls=Char, output_cls=Token,
                                     skips=["WHITESPACE"])),
        MODULE("mb4", META_BUILDER_4(name="function", fun="_function", input_cls=Char, output_cls=Token)),
        MODULE("mb5", META_BUILDER_5(name="function", fun="_function", input_cls=Char, output_cls=Token)),
    )
    print(package)
    package.save(allow_overwrite=True)


if __name__ == '__main__':
    main()
