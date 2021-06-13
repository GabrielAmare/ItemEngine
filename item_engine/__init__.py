"""
item_engine :
    generic engine maker for parsing
"""
from .constants import *
from .rules import *
from .items import *
from .elements import *
#from .ParserConfig import ParserConfig
from .build import *


# Optional = Optional.make
# Repeat = Repeat.make
# All = All.make
# Any = Any.make
# BranchSet = BranchSet.make


def include(group: Group) -> Match:
    return Match(group, INCLUDE)


def exclude(group: Group) -> Match:
    return Match(group, EXCLUDE)
