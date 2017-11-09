# Limitations:
#   - (* +++ *) serves as a separator of imports/exports from SML source,
#               assumed to be on a line by itself
#   - each import and export statement is assumed to be on a line by itself

import os
from string import Template

class Parser:
    # config
    SEP = '(* +++ *)' # assumed to be on a line by itself
    BASIS = '$(SML_LIB)/basis/basis.mlb' # default MLBasis
    EXT = {
            '.smlb': ('.sml', '.mlb'),
            '.funb': ('.fun', '.mlb'),
            '.sigb': ('.sig', '.mlb')
          }

    IMPORTS = '''
        local
            $builtin_bases
            $unfiltered_bases
            $filtered_bases
            open $all_bases
        in
            $module
        end\n'''

    EXPORTS = '''
        local
            $module_imports
        in
            $module_exports
        end'''

    BASEXP = 'basis $bas_id = bas $path end'

    LETBAS = '''
        basis $bas_id =
            let
                $path
            in
                bas
                    $ids
                end
            end\n'''

    def __init__(self, args):
        self.in_dir = os.path.normpath(args.src)
        self.out_dir = os.path.normpath(args.out_dir)

        # TODO: preprocess ignore file list & copy flag
        self.ignore= args.ignore
        self.copy = args.copy

        self.parse()

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

                    self.write_build(bases, unfiltered, filtered, exports, outdir, base, smlext, buildext)
                    self.write_sml(lines, sml_start, outdir, base, smlext)

    def _parse(self, lines, start):
        bases = [] # list of MLBases to import
        unfiltered = [] # list of paths to import, TODO: resolve
        filtered = [] # list of tuples (path, [id,...]) for filtered imports
        exports = []

        # TODO
        for line in lines:
            line = line.strip()
            # exports
            if line.startswith('export'):
                exports.extend(line[len('export'):].strip().strip('()').split(','))

            elif line.startswith('import'):
                line = line[len('import'):].strip()

                if line.startswith('$'):  # basis
                    bases.append(line)
                elif line.startswith('('): # filtered
                    filter_end = line.find('from')
                    path = line[filter_end+len('from'):].strip()
                    ids = line[:filter_end].strip().strip('()').split(',')
                    filtered.append((path, ids))
                elif line: # unfiltered path
                    unfiltered.append(line)
                else:
                    raise Exception("Unexpected import format...")
            else: continue # TODO: handle errors

        if not bases:
            bases.append(self.BASIS) # default basis

        return bases, unfiltered, filtered, exports


    def write_sml(self, lines, start, outdir, basename, ext):
        # TODO: add line directives
        outsml = os.path.join(outdir, basename) + ext
        with open (outsml, 'w') as outfile:
            outfile.writelines(lines[start:])

    def write_build(self, bases, unfiltered, filtered, exports, outdir, basename, smlext, buildext):
        # TODO: indent templates properly with textwrap module
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
        builtin_bases = '\n'.join(builtin_bases)

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
        unfiltered_bases = '\n'.join(unfiltered_bases)

        # bases of type (functor X, structure Z = Y) from "../path/to/moduleB.funb"
        filtered_bases = []
        counter = 0
        for (basis, identifiers) in filtered:
            path = self.format_mlb_path(basis)
            ids = '\n'.join([identifier for identifier in identifiers])
            bas = Template(self.LETBAS)
            binding = 'f'+str(counter)
            all_bases.append(binding)
            bas = bas.safe_substitute(bas_id=binding, path=path, ids=ids)
            filtered_bases.append(bas)
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
                module_imports=imports,
                module_exports='\n'.join(exports)
            )
        else:
            mlb = imports

        # write out MLB file
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
