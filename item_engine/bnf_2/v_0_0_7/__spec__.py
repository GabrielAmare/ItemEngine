from .engine import *

Grammar('"bnf"', '"0.0.5"', '" \\n\\t"',
        [Charset('digits', [Str("'0123456789'")]), Charset('letters', [Str("'abcdefghijklmnopqrstuvwxyz'")]),
         Charset('LETTERS', [Str("'ABCDEFGHIJKLMNOPQRSTUVWXYZ'")]),
         Charset('alpha', [Var('letters'), Var('LETTERS'), Str("'_'")]),
         Charset('alphanum', [Var('alpha'), Var('digits')]), Charset('sq', [Str('"\'"')]),
         Charset('dq', [Str('\'"\'')]), Pattern('VAR', [Var('alpha'), Var('alphanum')]),
         Operator('Str', MatchAs('STR', 'expr')), Operator('Var', MatchAs('VAR', 'name')),
         Operator('Match', All([Str("'{'"), MatchAs('VAR', 'name'), Str("'}'")])),
         Operator('MatchAs', All([Str("'{'"), MatchAs('VAR', 'name'), Str("' !'"), MatchAs('VAR', 'key'), Str("'}'")])),
         Operator('MatchIn', All([Str("'{'"), MatchAs('VAR', 'name'), Str("' *'"), MatchAs('VAR', 'key'), Str("'}'")])),
         Operator('All', EnumP(Str("' '"), MatchIn('Atom_', 'args'))),
         Operator('Any', EnumP(Str("' | '"), MatchIn('All_', 'args'))),
         Operator('Optional', All([Str("'['"), MatchAs('Any_', 'child'), Str("']'")])),
         Operator('Repeat', All([Str("'('"), MatchAs('Any_', 'child'), Str("')'")])),
         Operator('Enum', All([MatchAs('Str', 'separator'), Str("'.'"), MatchAs('MatchIn', 'child')])),
         Operator('EnumP', All([MatchAs('Str', 'separator'), Str("'^'"), MatchAs('MatchIn', 'child')])),
         Operator('Charset', All(
             [Str("'c:'"), MatchAs('VAR', 'name'), Str("' = '"), Enum(Str("' '"), MatchIn('CharsetArg', 'args'))])),
         Operator('Pattern', All(
             [Str("'p:'"), MatchAs('VAR', 'name'), Str("' = '"), Enum(Str("' '"), MatchIn('PatternArg', 'args'))])),
         Operator('Operator', All([Str("'o:'"), MatchAs('VAR', 'name'), Str("' = '"), MatchAs('Any_', 'rule')])),
         Operator('Group', All(
             [Str("'g:'"), MatchAs('VAR', 'name'), Str("' = '"), EnumP(Str("' | '"), MatchIn('VAR', 'names'))])),
         Operator('Grammar', All(
             [Str("'@lang:'"), MatchAs('STR', 'lang'), Str("'\\n'"), Str("'@version:'"), MatchAs('STR', 'version'),
              Str("'\\n'"), Str("'@whitespace:'"), MatchAs('STR', 'whitespace'), Str("'\\n'"),
              Enum(Str("'\\n'"), MatchIn('GrammarArg', 'args'))])), Group('CharsetArg', ['Str', 'Var']),
         Group('PatternArg', ['Str', 'Var']), Group('GrammarArg', ['Operator', 'Group', 'Charset', 'Pattern']),
         Group('Atom_', ['Str', 'Match', 'MatchAs', 'MatchIn', 'Enum', 'EnumP', 'Optional', 'Repeat']),
         Group('All_', ['Atom_', 'All']), Group('Any_', ['All_', 'Any'])])
