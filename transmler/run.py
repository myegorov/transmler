from .cli import cli
from .parser import Parser

def main():
    args = cli()
    Parser(args).parse()

if __name__ == "__main__":
    main()
