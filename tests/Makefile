SML:=mlton
ROOT:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: example
example: src/example.smlb src/stack.smlb src/stack.sigb
	export SMLPATH="$(ROOT)/src:$(ROOT)/sml_modules"
	transmile src --out-dir dist --copy-files --ignore README
	$(SML) -show-basis basis -prefer-abs-paths true -show-def-use def-use -stop tc ./dist/example.sml.mlb
	# $(SML) -show-def-use def-use -prefer-abs-paths true -output example ./dist/example.sml.mlb
