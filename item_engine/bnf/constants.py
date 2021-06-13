import os

GRAMMAR_PATH = os.path.join(__file__, '../grammar')

SYMBOL_TABLE = {
    '=': 'EQUAL', '+': 'PLUS', '-': 'DASH', '*': 'STAR', '/': 'SLASH', '_': 'UNSC', '|': 'VBAR', '&': 'AMPS',
    '#': 'SHARP', '@': 'AT', '^': 'HAT', '%': 'PERCENT', '~': 'WAVE', '\\': 'CSLASH', ',': 'COMMA', '.': 'DOT',
    '!': 'EXC', '?': 'INTER', ':': 'COLON', ';': 'SEMICOLON', '<': 'LV', '>': 'RV', '(': 'LP', ')': 'RP', '[': 'LB',
    ']': 'RB', '{': 'LS', '}': 'RS', '"': 'DQ', "'": 'SQ', '$': 'DOLLAR', '€': 'EURO', '£': 'POUND', '\n': 'NEWLINE',
    '⁰': 'POW0', '¹': 'POW1', '²': 'POW2', '³': 'POW3', '⁴': 'POW4', '⁵': 'POW5', '⁶': 'POW6', '⁷': 'POW7', '⁸': 'POW8',
    '⁹': 'POW9', '∀': 'FORALL', '∃': 'EXIST', '∈': 'ISIN', '∉': 'NOTIN', '∋': 'NI', '∩': 'CAP', '∪': 'CUP', '⊂': 'SUB',
    '⊃': 'SUP', '⊄': 'NSUB', '⊆': 'SUBE', '⊇': 'SUPE', '∧': 'AND', '∨': 'OR', '≡': 'EQUIV', '∴': 'THERE4', '⊕': 'OPLUS',
    '⊗': 'OTIMES', '⊥': 'PERP', '◊': 'LOZ', '∂': 'PART', '∅': 'EMPTY', '∇': 'NABLA', '∏': 'PROD', '∑': 'SUM',
    '−': 'MINUS', '∗': 'LOWAST', '√': 'RADIC', '⋅': 'SDOT', '∝': 'PROP', '∞': 'INFIN', '∠': 'ANG', '∫': 'INT',
    '∼': 'SIM', '≅': 'CONG', '≈': 'ASYMP', '≠': 'NE', '≤': 'LE', '≥': 'GE', '␄': 'EOT'
}
