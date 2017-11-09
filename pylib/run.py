#!/usr/bin/env python

import cli
from parser import Parser

if __name__ == "__main__":
    args = cli.main()
    Parser(args).parse()
