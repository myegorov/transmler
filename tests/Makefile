SML=mlton

.PHONY: example
example: src/example.smlb src/stack.smlb src/stack.sigb
	transmile src --out-dir dist --copy-files --ignore README
	$(SML) -stop tc ./dist/example.sml.mlb
	$(SML) -show-def-use defuse -prefer-abs-paths true -output example ./dist/example.sml.mlb
