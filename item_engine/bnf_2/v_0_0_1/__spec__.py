from .engine import *

Name = MatchAs("VAR", "name")
Names = MatchIn("VAR", "names")
Key = MatchAs("VAR", "key")
Content = MatchAs("STR", "content")

grammar = Grammar(
    "bnf",
    "0.0.0",
    [
        Operator("Str", Content),

        Operator("Match", All([Str("'{'"), Name, Str("'}'")])),
        Operator("MatchAs", All([Str("'{'"), Name, Str("' !'"), Key, Str("'}'")])),
        Operator("MatchIn", All([Str("'{'"), Name, Str("' *'"), Key, Str("'}'")])),

        Operator("All", Enum(Str("' '"), MatchIn("Atom_", "args"))),
        Operator("Any", Enum(Str("' | '"), MatchIn("All_", "args"))),

        Operator("Optional", All([Str("'['"), MatchAs("Any_", "child"), Str("']'")])),
        Operator("Repeat", All([Str("'('"), MatchAs("Any_", "child"), Str("')'")])),

        Operator("Enum", All([MatchAs("Str", "separator"), Str("'.'"), MatchAs("MatchIn", "child")])),

        Operator("Operator", All([Name, Str("' = '"), MatchAs("Any_", "rule")])),
        Operator("Charset", All([Str("'charset:'"), Name, Str("' = '"), MatchAs("STR", "expr")])),
        Operator("Group", All([Name, Str("' > '"), Enum(Str("' | '"), Names)])),

        Operator("Grammar", Enum(Str("'\\n'"), MatchIn("GrammarRule", "branches"))),

        Group("GrammarRule", ["Operator", "Group"]),

        Group("Atom_", ["Str", "Match", "MatchAs", "MatchIn", "Enum", "Optional", "Repeat"]),
        Group("All_", ["Atom_", "All"]),
        Group("Any_", ["All_", "Any"]),
    ]
)
