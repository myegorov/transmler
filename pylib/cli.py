import argparse
import sys
import os

class ArgParser(argparse.ArgumentParser):
    def error(self, msg):
        sys.stderr.write('%s\n' %msg)
        self.print_help()
        sys.exit(1)

    def read_dir(dir_path):
        if not os.path.isdir(dir_path):
            raise argparse.ArgumentTypeError("{0} directory does not exist".format(dir_path))
        if os.access(dir_path, os.R_OK):
            return dir_path
        else:
            raise argparse.ArgumentTypeError("Cannot read {0} directory".format(dir_path))

    # TODO: copy directory permissions from source
    # https://docs.python.org/3.6/library/os.html#os.mkdir
    # https://stackoverflow.com/questions/5337070/how-can-i-get-a-files-permission-mask/5337329#5337329
    def write_dir(dir_path):
        os.makedirs(dir_path, exist_ok=True)
        if os.access(dir_path, os.W_OK):
            return dir_path
        else:
            raise argparse.ArgumentTypeError("Cannot write to {0} directory".format(dir_path))


def main():
    parser = ArgParser()
    parser.add_argument('src', type=ArgParser.read_dir,
                        help='transpile files in the source directory')
    parser.add_argument('-d', '--out-dir', type=ArgParser.write_dir,
                        help='output to the directory')
    _parser = parser.add_mutually_exclusive_group(required=False)
    _parser.add_argument('-c', '--copy-files', dest='copy', action='store_true',
                        help='copy the files that will not be transpiled')
    _parser.add_argument('-n', '--no-copy-files', dest='copy', action='store_false',
                        help='do not copy files that will not be transpiled')
    parser.add_argument('-i', '--ignore', type=str, dest='ignore',
                        help='list of comma-separated file names to ignore')
    parser.set_defaults(copy=True, ignore="")

    return parser.parse_args()
