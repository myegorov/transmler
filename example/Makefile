SML:=~/opt/usr/bin/mlton
ROOT:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
export SMLPATH="$(ROOT)src:$(ROOT)sml_modules"

.PHONY: example
example: src/example.smlb src/stack.smlb src/stack.sigb
	transmile src --imports --out dist/src --skip README
	$(SML) -show-basis-verbose basis -prefer-abs-paths true -show-def-use def-use -stop tc ./dist/src/._example.sml.mlb
	# $(SML) -output example ./dist/src/example.sml.mlb
