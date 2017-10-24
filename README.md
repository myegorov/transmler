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
behind the scenes.

# Roadmap

- specify the DSL for imports (`qualified, unqualified, hiding`)
    and exports and some trivial examples; think about what this would
    look like if there was an `npm`-like package manager to pull in
    third-party dependencies to some per project `sml-modules` directory;
- lexer + parser to _transmile_ the DSL sources to target `*.sig`/`*.sml`/`*.fun`;
- think about how to provide bi-directional source maps between the DSL 
    original and _transmiled_ sources for debugging;
- `ctags`-like tooling for jumping between the definitions and uses in
    the DSL sources;
