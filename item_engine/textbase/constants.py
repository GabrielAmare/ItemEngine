import python_generator as pg
from .functions import *
from .materials import SymbolMaker

__all__ = [
    "digits", "digits_pow", "digits_bin", "digits_oct", "digits_hex",
    "letters", "LETTERS", "alpha", "alphanum",
    "dot",
    "n_alphanum",
    "sq", "dq", "n_sq", "n_dq", "e_sq", "e_dq",
    "INT_POW_TO_INT"
]

# USEFUL CHARSETS
digits = charset("0123456789").inc()
digits_pow = charset("⁰¹²³⁴⁵⁶⁷⁸⁹").inc()
digits_bin = charset("01").inc()
digits_oct = charset("01234567").inc()
digits_hex = charset('0123456789' + 'abcdef' + 'ABCDEF').inc()

letters = charset('abcdefghijklmnopqrstuvwxyz').inc()
LETTERS = charset('ABCDEFGHIJKLMNOPQRSTUVWXYZ').inc()
alpha = charset('abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + '_').inc()
alphanum = charset('abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + '_' + '0123456789').inc()

dot = charset(".").inc()

n_alphanum = (~alphanum.group).inc()

sq = charset("'").inc()
dq = charset('"').inc()

n_sq = (~sq.group).inc()
n_dq = (~dq.group).inc()
e_sq = string("\\'")
e_dq = string('\\"')

# DEFAULT SYMBOL MAKER WITH BASE NAMES
symbol_maker = SymbolMaker(
    EQUAL="=", PLUS="+", DASH="-", STAR="*", SLASH="/", UNSC="_", VBAR="|", AMPS="&",
    SHARP="#", AT="@", HAT="^", PERCENT="%", WAVE="~", CSLASH="\\",
    COMMA=",", DOT=".", EXC="!", INTER="?", COLON=":", SEMICOLON=";",
    LV="<", RV=">", LP="(", RP=")", LB="[", RB="]", LS="{", RS="}", DQ='"', SQ="'",
    DOLLAR="$", EURO="€", POUND="£", NEWLINE='\n',
    POW0="⁰", POW1="¹", POW2="²", POW3="³", POW4="⁴", POW5="⁵", POW6="⁶", POW7="⁷", POW8="⁸", POW9="⁹",
    # Maths Sets Symbols
    FORALL="∀", EXIST="∃", ISIN="∈", NOTIN="∉", NI="∋",
    CAP="∩", CUP="∪", SUB="⊂", SUP="⊃", NSUB="⊄", SUBE="⊆", SUPE="⊇",
    # Maths Logic Symbols
    AND="∧", OR="∨", EQUIV="≡", THERE4="∴", OPLUS="⊕", OTIMES="⊗", PERP="⊥", LOZ="◊",
    # Other Misc Maths Symbols
    PART="∂", EMPTY="∅", NABLA="∇", PROD="∏", SUM="∑", MINUS="−", LOWAST="∗", RADIC="√", SDOT="⋅",
    PROP="∝", INFIN="∞", ANG="∠", INT="∫", SIM="∼", CONG="≅", ASYMP="≈", NE="≠", LE="≤", GE="≥",
)

_POW_INT_CHARS = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9"}
_POW_INT_ORDS = {ord(k): ord(v) for k, v in _POW_INT_CHARS.items()}

# PARSE FUNCTION FOR POWER INTEGERS
INT_POW_TO_INT = pg.LAMBDA(
    args=["content"],
    expr=pg.VAR("content").GETATTR("translate").CALL(pg.DICT(_POW_INT_ORDS))
)
