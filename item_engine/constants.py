from typing import Union, Tuple

__all__ = [
    "NT_STATE", "T_STATE", "STATE",
    "INDEX", "POSITION",
    "ACTION", "INCLUDE", "EXCLUDE", "AS", "IN",
    "CASE",
]

ACTION = str
NT_STATE = int
T_STATE = str
STATE = Union[NT_STATE, T_STATE]

INDEX = int
POSITION = int

INCLUDE: ACTION = "∈"
EXCLUDE: ACTION = "∉"
AS: ACTION = "as:{}"
IN: ACTION = "in:{}"

CASE = Tuple[ACTION, STATE]
