import sys
from time import perf_counter
from getpass import getpass
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from .core import Sha256
from .utils import read_file_input
from . import __version__

def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Pure Python SHA-256 hashing implementation",
        formatter_class=RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  sha256py 'hello'         # hash a string\n"
            "  sha256py -f file.txt     # hash contents of a file\n"
            "  sha256py --silent        # silent prompt for input\n"
            "  sha256py --raw           # output raw binary digest\n"
            "  sha256py --time          # show hashing duration\n"
            "  sha256py -               # read input from stdin"
        )
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("input", nargs="?", help="Input string or '-' for stdin")
    parser.add_argument("-f", "--file", help="Read input from file")
    parser.add_argument("--silent", action="store_true", help="Silent prompt for input")
    parser.add_argument("--raw", action="store_true", help="Output raw digest")
    parser.add_argument("--binary", action="store_true", help="Output binary digest")
    parser.add_argument("--time", action="store_true", help="Display time taken to compute hash")
    parser.add_argument("-l", "--log", action="store_true", help="Educational log of the hashing process")
    return parser

def get_input_string(args) -> str:
    if args.file:
        return read_file_input(args.file)
    elif args.silent:
        return getpass("Enter string to hash: ")
    elif args.input == "-":
        return sys.stdin.read()
    elif args.input:
        return args.input
    else:
        return input("Enter string to hash: ")

def compute_hash(input_str: str, log_func) -> dict:
    hasher = Sha256(input_str, log_func=log_func)
    return {
        "digest": hasher.digest(),
        "hex": hasher.hexdigest(),
        "bin": hasher.bindigest(),
    }

def print_output(results: dict, args):
    if args.raw:
        if sys.stdout.isatty():
            print("[Warning] Raw binary output may look garbled in your terminal.\n"
                  "Use `> file.bin` to redirect.", file=sys.stderr)
        sys.stdout.buffer.write(results["digest"])
    elif args.binary:
        print(results["bin"])
    else:
        print(results["hex"])

def main():
    parser = build_parser()
    args = parser.parse_args()
    log = print if args.log else None

    try:
        input_str = get_input_string(args)
    except Exception as e:
        print(f"[Error] {e}", file=sys.stderr)
        sys.exit(1)

    start = perf_counter()
    results = compute_hash(input_str, log_func=log)
    end = perf_counter()

    print_output(results, args)

    if args.time:
        duration = (end - start) * 1000
        print(f"[Time] Hash computed in {duration:.2f} ms")
