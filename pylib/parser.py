import os

class Parser:

    EXT = {
            '.smlb': ('.sml', '.mlb'),
            '.funb': ('.fun', '.mlb'),
            '.sigb': ('.sig', '.mlb')
          }

    SEP = '(* +++ *)' # assumed to be on a line by itself

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
                    lines = infile.readlines()
                    print (lines)

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
