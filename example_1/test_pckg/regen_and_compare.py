from example_1.test_pckg.make import engine


def main(repeats: int = 100):
    old = None

    for repeat in range(repeats):
        engine.build(allow_overwrite=True)

        with open("engine/lexer.py") as file:
            new = file.read()

        if old is not None:
            assert old == new

        old = new
        print(f"{repeat + 1}/{repeats}")


if __name__ == '__main__':
    main()
