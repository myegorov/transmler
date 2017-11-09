import argparse
import sys
import os

class ArgParser(argparse.ArgumentParser):
    def error(self, msg):
        sys.stderr.write('\n%s\n\n' %msg)
        self.print_help()
        sys.exit(1)

    def read_dir(dir_path):
        if not os.path.isdir(dir_path):
            raise argparse.ArgumentTypeError(
                "\n{0} directory does not exist".format(dir_path))
        if os.access(dir_path, os.R_OK):
            return dir_path
        else:
            raise argparse.ArgumentTypeError(
                "\nCannot read {0} directory".format(dir_path))

    def write_dir(dir_path):
        os.makedirs(dir_path, exist_ok=True)
        if os.access(dir_path, os.W_OK):
            return dir_path
        else:
            raise argparse.ArgumentTypeError(
                "\nCannot write to {0} directory".format(dir_path))


def main():
    parser = ArgParser()
    parser.add_argument('src', type=ArgParser.read_dir,
                        help='transpile files in the source directory')
    exclusive_group = parser.add_mutually_exclusive_group(required=False)
    exclusive_group.add_argument('-c', '--copy-files', 
                        dest='copy', action='store_true',
                        help='copy the files that will not be transpiled (default)')
    exclusive_group.add_argument('-n', '--no-copy-files', 
                        dest='copy', action='store_false',
                        help='do not copy files that will not be transpiled')
    parser.add_argument('-i', '--ignore', type=str, dest='ignore',
                        help='list of comma-separated file names to ignore')
    req_opt = parser.add_argument_group('required named arguments')
    req_opt.add_argument('-d', '--out-dir', type=ArgParser.write_dir,
                        help='output to the directory', required=True)
    parser.set_defaults(copy=True, ignore="")

    return parser.parse_args()
