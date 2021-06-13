from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class TagStyle:
    foreground: str = 'white'
    background: str = 'black'


class TextStyle:
    def __init__(self, config: Dict[str, TagStyle]):
        self.config: Dict[str, TagStyle] = config

    def __getitem__(self, name: str) -> dict:
        if name in self.config:
            return asdict(self.config[name])
        else:
            return {}


def main():
    chart = TextStyle({
        'VAR': TagStyle(foreground='#2c68bd'),
        'STR': TagStyle(foreground='#0f9018'),

        'EXC': TagStyle(foreground='#f2a40f'),
        'STAR': TagStyle(foreground='#f2a40f'),
        'COMMENT': TagStyle(foreground='#c9b30a'),
        'ERROR': TagStyle(background='#d91d09'),

        'AS': TagStyle(foreground='#f2a40f'),
        'IN': TagStyle(foreground='#f2a40f'),
        'MATCH': TagStyle(foreground='#f2a40f'),
    })

    for tag in chart.config:
        print(chart[tag])


if __name__ == '__main__':
    main()
