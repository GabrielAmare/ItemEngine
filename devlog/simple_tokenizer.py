from typing import List, Tuple, Dict
import re

patterns: Dict[str, re.Pattern] = {
    'MOT': re.compile(r"[a-zA-Z]+"),
    'NUMBER': re.compile(r"[0-9]+"),
    'ESPACE': re.compile(r"[ ]+"),
    'PLUS': re.compile(r"\+"),
    'MULTIPLIER': re.compile(r"\*"),
    'QUESTION': re.compile(r"\?"),
}


def tokenize(text: str) -> List[Tuple[str, str]]:
    tokens: List[Tuple[str, str]] = []
    index = 0
    while index < len(text):
        for name, pattern in patterns.items():
            match = pattern.match(text[index:])
            if match:
                content = match.group()
                index += len(content)
                if name != "ESPACE":
                    tokens.append((name, content))
                continue
    return tokens


if __name__ == '__main__':
    tokens = tokenize("Quel est le resultat de 5 + 36 * 15 ?")
    for token in tokens:
        print(token)
