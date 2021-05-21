from install37 import setup
from item_engine.__meta__ import __version__

if __name__ == "__main__":
    setup(
        name="item_engine",
        version=__version__,
        author="Gabriel Amare", 
        author_email="gabriel.amare.dev@gmail.com",
        description="generic engine maker for parsing", 
        url="https://github.com/GabrielAmare/ItemEngine",
        packages=[
            "item_engine",
            "item_engine.builders",
            "item_engine.textbase",
            "item_engine.textbase.items",
        ],
        classifiers=[], 
        python_requires=">=3.7"
    )
