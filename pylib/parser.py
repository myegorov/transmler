# Limitations:
#   - (* +++ *) serves as a separator of imports/exports from SML source,
#               assumed to be on a line by itself
#   - each import and export statement is assumed to be on a line by itself

import os
from string import Template, whitespace
import textwrap as tw

class Parser:
    # config
    SEP = '(* +++ *)' # assumed to be on a line by itself
    BASIS = '$(SML_LIB)/basis/basis.mlb' # default MLBasis

    # use input file suffix to determine the output file suffix
    EXT = {
            '.smlb': ('.sml', '.mlb'),
            '.funb': ('.fun', '.mlb'),
            '.sigb': ('.sig', '.mlb')
          }

    IMPORTS = tw.dedent('''
        local
          $builtin_bases
          $unfiltered_bases
          $filtered_bases
          open $all_bases
        in
          $module
        end''')

    EXPORTS = tw.dedent('''
        local
          $module_imports
        in
          $module_exports
        end''')

    BASEXP = 'basis $bas_id = bas $path end'

    LETBAS = tw.dedent('''
        basis $bas_id =
          let
            $path
          in
            bas
              $ids
            end
          end''')
    TAB = '  ' # indent each level by two spaces

    MASK = str.maketrans({'(':'', ')':''}) # strip out parens

    def __init__(self, args):
        self.in_dir = os.path.normpath(args.src)
        self.out_dir = os.path.normpath(args.out_dir)


        # TODO: preprocess ignore file list & copy flag
        self.ignore= args.ignore
        self.copy = args.copy


    def parse(self):
        for (infile_path, fname, outdir) in self.walk_dirs():
            if self.is_stale(infile_path, fname, outdir):
                with open(infile_path, 'r') as infile:
                    base, ext = os.path.splitext(fname)
                    smlext, buildext = self.EXT[ext]
                    split_line, lines = self.find_split(infile)
                    if split_line < 0:
                        bases = [self.BASIS] # default basis
                        unfiltered, filtered, exports = [], [], []
                        sml_start = 0 # write out all lines starting with line 0
                    else:
                        bases, unfiltered, filtered, exports = self._parse(lines, split_line)
                        sml_start = split_line + 1

                    # write out .mlb, .sml etc
                    self.write_build(bases, unfiltered, filtered, exports, outdir, base, smlext, buildext)
                    self.write_sml(lines, sml_start, outdir, base, smlext)

    def _parse(self, lines, start):
        bases = [] # list of MLBases to import
        unfiltered = [] # list of paths to import, TODO: resolve
        filtered = [] # list of tuples (path, [id,...]) for filtered imports
        exports = []


        for line in lines:
            line = line.strip()
            if line.startswith('export'):
                ids = [identifier.translate(self.MASK).strip() \
                        for identifier in line[len('export'):].split(',')]
                exports.extend(ids)

            elif line.startswith('import'):
                line = line[len('import'):].strip()

                if line.startswith('$'):  # basis
                    bases.append(line)
                elif line.startswith('('): # filtered
                    # instead of requiring that 'from' be reserved keyword,
                    #   match parens
                    filter_end = self.find_matching_paren(line)
                    if filter_end < 1:
                        raise Exception("Unlosed parenthesis in import block?")
                    remainder = line[filter_end+1:].strip()
                    if not remainder.startswith('from'):
                        raise Exception("Expected 'from' in import")
                    path = remainder[len('from'):].strip()
                    ids = [identifier.translate(self.MASK).strip() \
                            for identifier in line[:filter_end+1].split(',')]

                    filtered.append((path, ids[:]))
                elif line: # unfiltered path
                    unfiltered.append(line)
                else:
                    raise Exception("Unexpected import format...")
            # not robust, will skip newlines & comments,
            #       but also any unintended errors
            else: continue

        if not bases:
            bases.append(self.BASIS) # default basis

        return bases, unfiltered, filtered, exports

    def find_matching_paren(self, line):
        ''' Returns index in line of closing parenthesis
        '''
        ix, counter = 1, 1
        for char in line[1:]:
            if char == '(':
                counter += 1
            elif char == ')':
                counter -= 1
                if counter < 1: break
            ix += 1
        return ix if ix < len(line) else -1

    def write_sml(self, lines, start, outdir, basename, ext):
        # TODO: add line directives
        outsml = os.path.join(outdir, basename) + ext
        with open (outsml, 'w') as outfile:
            outfile.writelines(lines[start:])

    def write_build(self, bases, unfiltered, filtered, exports, outdir, basename, smlext, buildext):
        # TODO: add line directives
        all_bases = []

        # bases of type $(SML_LIB)/...
        builtin_bases = []
        counter = 0
        for basis in bases:
            bas = Template(self.BASEXP)
            binding = 'b'+str(counter)
            all_bases.append(binding)
            bas = bas.safe_substitute(bas_id=binding, path=basis)
            builtin_bases.append(bas)
            counter += 1
        builtin_bases = '\n' + tw.indent('\n'.join(builtin_bases), self.TAB)

        # bases of type "/path/to/moduleA.sigb"
        unfiltered_bases = []
        counter = 0
        for basis in unfiltered:
            path = self.format_mlb_path(basis)
            bas = Template(self.BASEXP)
            binding = 'u'+str(counter)
            all_bases.append(binding)
            bas = bas.safe_substitute(bas_id=binding, path=path)
            unfiltered_bases.append(bas)
            counter += 1
        unfiltered_bases = '\n' + tw.indent('\n'.join(unfiltered_bases), self.TAB)

        # bases of type (functor X, structure Z = Y) from "../path/to/moduleB.funb"
        filtered_bases = []
        counter = 0
        for (basis, identifiers) in filtered:
            path = self.format_mlb_path(basis)
            ids = '\n' + tw.indent('\n'.join([identifier for identifier in identifiers]), 3*self.TAB)
            bas = Template(self.LETBAS)
            binding = 'f'+str(counter)
            all_bases.append(binding)
            bas = bas.safe_substitute(bas_id=binding, path=path, ids=ids)
            filtered_bases.append(tw.indent(bas, self.TAB))
            counter += 1
        filtered_bases = '\n'.join(filtered_bases)

        # create imports block of MLB
        imports = Template(self.IMPORTS)
        imports = imports.safe_substitute( # convert Template to string
            builtin_bases=builtin_bases,
            unfiltered_bases=unfiltered_bases,
            filtered_bases=filtered_bases,
            all_bases=' '.join(all_bases),
            module=basename+smlext
        )

        # create exports block of MLB
        if exports:
            mlb = Template(self.EXPORTS)
            mlb = mlb.safe_substitute( # convert Template to string
                module_imports=tw.indent(imports, self.TAB),
                module_exports='\n' + tw.indent('\n'.join(exports), self.TAB)
            )
        else:
            mlb = imports

        # write out MLB file
        mlb = (os.linesep).join([line for line in mlb.splitlines() if line.rstrip()])
        outmlb = os.path.join(outdir, basename) + smlext + buildext
        with open (outmlb, 'w') as outfile:
            outfile.write(mlb)

    def format_mlb_path(self, orig_path):
        orig_path = orig_path.strip('"\'')
        base, ext = os.path.splitext(orig_path)
        if ext not in self.EXT:
            raise Exception ("\nEncountered unknown file extension {0}".format(ext))
        smlext, buildext = self.EXT[ext]
        path = base + smlext + buildext
        return path

    def find_split(self, infile):
        lines = infile.readlines()
        split_line = -1 # flag if not found
        for i, line in enumerate(lines):
            if self.SEP in line:
                split_line = i
                break
        return split_line, lines

    def is_stale(self, infile_path, fname, outdir):
        ''' Returns True if infile needs to be transpiled else False.
        '''
        base, ext = os.path.splitext(fname)

        if ext not in self.EXT:
            raise Exception ("\nEncountered unknown file extension {0}".format(ext))
        smlext, buildext = self.EXT[ext]
        outsml = os.path.join(outdir, base, smlext)
        outbuild = os.path.join(outdir, base, buildext)
        if os.path.isfile(outsml) and os.path.isfile(outbuild) and \
                os.path.getmtime(outsml) > os.path.getmtime(infile_path) and \
                os.path.getmtime(outbuild) > os.path.getmtime(infile_path):
            return False # outfiles are more recent than source
        else:
            return True

    def walk_dirs(self):
        ''' Walk self.in_dir and create same structure in self.out_dir
        '''
        base_len = len(self.in_dir.split(os.sep))
        for indir, dirs, files in os.walk(self.in_dir):
            suffix = os.sep.join(indir.split(os.sep)[base_len:])
            outdir = os.path.join(self.out_dir, suffix)
            os.makedirs(outdir, exist_ok=True)
            for f in files:
                infile = os.path.join(indir, f)
                yield (infile, f, outdir)
