from sys import argv
from .core import Sha256

def main():
    # Help flag
    if len(argv) > 1 and argv[1].lower() in ("-h", "--help"):
        print("Pure Python SHA-256 hashing implementation")
        print("\tUsage: python -m sha256py [string]")
        print("\tIncase no string is provided, you will be prompted to enter one.")
        return

    # Get input from argument or prompt
    if len(argv) > 1:
        input_str = argv[1]
    else:
        try:
            input_str = input("Enter string to hash: ")
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            return

    hash_obj = Sha256(input_str)
    print(hash_obj.hexdigest())