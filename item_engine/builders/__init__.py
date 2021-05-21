from typing import Type, List
from .. import Element
from .MB1 import META_BUILDER_1
from .MB3 import META_BUILDER_3
from .MB4 import META_BUILDER_4
from .MB5 import META_BUILDER_5

FORMAL_INPUTS = 1
FORMAL_OUTPUTS = 2
HAS_SKIPS = 4
REFLEXIVE = 8


def build_func(name: str,
               fun: str,
               formal_inputs: bool,
               formal_outputs: bool,
               reflexive: bool,
               input_cls: Type[Element],
               output_cls: Type[Element],
               skips: List[str] = None):
    has_skips = bool(skips)
    sign = FORMAL_INPUTS * formal_inputs + FORMAL_OUTPUTS * formal_outputs + HAS_SKIPS * has_skips + REFLEXIVE * reflexive

    if sign == FORMAL_INPUTS + FORMAL_OUTPUTS:
        return META_BUILDER_1(name=name, fun=fun, input_cls=input_cls, output_cls=output_cls)
    elif sign == FORMAL_INPUTS + FORMAL_OUTPUTS + HAS_SKIPS:
        return META_BUILDER_3(name=name, fun=fun, input_cls=input_cls, output_cls=output_cls, skips=skips)
    elif sign == FORMAL_INPUTS:
        return META_BUILDER_4(name=name, fun=fun, input_cls=input_cls, output_cls=output_cls)
    elif sign == FORMAL_INPUTS + REFLEXIVE:
        return META_BUILDER_5(name=name, fun=fun, input_cls=input_cls, output_cls=output_cls)
    else:
        raise Exception("invalid parameters combination")


__all__ = ["build_func"]
