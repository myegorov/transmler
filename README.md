# What

SML compilers, such as [MLton](http://mlton.org/MLBasis) and
[SML/NJ](http://www.smlnj.org/doc/CM/new.pdf), are designed to
relieve the programmer to a large extent from managing the dependency
graph of individual source files, beyond specifying the imports and
exports, typically for a group of source files constituting a library
component.

Depending on one's workflow and the project's complexity,
the cognitive load on the programmer may in fact be minimized by
keeping the import and export statements within the context of
the module where they apply. In this approach, the link between the
declarations and their uses is made explicit. In addition, one can
incrementally type check the program one file at a time,
as suggested in https://sourceforge.net/p/mlton/mailman/message/31513087/

The goal is to develop a proof of concept for a transpiler step added to
an [MLBasis](http://mlton.org/MLBasis) based compilation workflow and test 
it on a non-trivial SML project. It should be emphasized
that no changes are planned to how MLBasis manages the namespaces
behind the scenes. A subset of 
[MLBasis](http://mlton.org/MLBasisSyntaxAndSemantics) constructs
will be supported (excluding `ann`).


# Use case

The `transmile` utility may be invoked as in the following
`Makefile` target:
```shell
SML=mlton

.PHONY: foo
foo: src/foo.smlb
	transmile src --out-dir dist --copy-files --ignore README
	$(SML) -stop tc ./dist/foo.sml.mlb
```

The `transmile` commandline utility (here assumed to be on the shell
search path) will pick up any `*.smlb`,
`*.sigb` or `*.funb` files in the `src` directory and transpile them into a 
set of `*.sml`, `*.sig`, or `*.fun` files in the `dist` directory, each
with a corresponding `*.mlb` MLBasis file.
With the above flags, it will also copy any files that it
didn't transpile, with the exception of explicitly excluded files.

`import` and `export` statements in a `*b` source file must come before any
SML program, except that SML-style comments (and line directives) are 
allowed within the import/export block.

The syntax for importing entities is any combination of:
```
import $(SML_LIB)/basis/basis-1997.mlb
import "/path/to/moduleA.sigb"
import (functor X, structure Z = Y) from "../path/to/moduleB.funb"
```

By default, every module will implicitly import the SML Basis library
(`$(SML_LIB)/basis/basis.mlb`), except where overriden by any explicit
`import $(SML_LIB)/...` directive as in the above example.

`transmile` will try to resolve any path (except any path from the
`$(SML_LIB)` root) in this order:
* searching the directory relative to the `*b` source file (except
    where an absolute path is specified);
* followed by the environment variable `SMLPATH` (set to, e.g.,
    `<project-root>/src:<project-root>/sml-modules` in the `Makefile`);
* followed by any installation-dependent default search path (shell `PATH`).

For example, resolving `import X.sigb` entails looking up `./X.sig.mlb`,
then `<($SMLPATH)>/X.sig.mlb`, then `<($PATH)>/X.sig.mlb`, and returning with
an error if none is found.

Assuming the above import statements are placed in an `example.smlb`, 
and that all the referenced `*.mlb` files can be found relative to the
location of `example.smlb`,
the outcome will be an `example.sml` file with the SML program, plus
an `example.sml.mlb` file:

```sml
local
  basis a = bas (*#line 1.8 "example.smlb"*)$(SML_LIB)/basis/basis-1997.mlb end
  basis b = bas (*#line 2.8 "example.smlb"*)"/path/to/moduleA.sig.mlb" end
  basis c =
    let
      (*#line 3.42 "example.smlb"*)"../path/to/moduleB.fun.mlb"
    in
      bas
        (*#line 3.9 "example.smlb"*)functor X
        (*#line 3.20 "example.smlb"*)structure Z = Y
      end
    end

  open a b c

in
  example.sml
end
```

The syntax for exporting entities is along the lines of:
```
export (signature K, structure M = L)
(* +++ *) (* for the time being, 3+ plus signs signal end of import/export block *)
```

Assuming this `export` statement follows the `import` statements in the
above `example.smlb`, the resulting `example.sml.mlb`
will contain:

```sml
local
  local
    basis a = bas (*#line 1.8 "example.smlb"*)$(SML_LIB)/basis/basis-1997.mlb end
    basis b = bas (*#line 2.8 "example.smlb"*)"/path/to/moduleA.sig.mlb" end
    basis c =
      let
        (*#line 3.42 "example.smlb"*)"../path/to/moduleB.fun.mlb"
      in
        bas
          (*#line 3.9 "example.smlb"*)functor X
          (*#line 3.20 "example.smlb"*)structure Z = Y
        end
      end

    open a b c
  in
    example.sml
  end

in
  (*#line 4.9 "example.smlb"*)signature K
  (*#line 4.22 "example.smlb"*)structure M = L
end
```

If an `export` statement were missing from `example.smlb`, the module
would effectively export all its top-level identifiers.


# Roadmap

- simple scripts for prototype
- `ctags`-like tooling for jumping between the definitions and uses in
    the DSL sources + autocomplete/show signature;
- specify the DSL grammar for imports and exports;
- `transmile` CLI tool (source, destination, ignore/copy, edit/print $SMLPATH)
- eventually lexer + parser;
