"""
Main function for appvault module.
For help, run this module with the -h parameter.
"""


import argparse
from pathlib import Path
from .encrypt import encrypt
from .run import run


def main():
    """Run the appvault client module.
    For help, run this module with the -h parameter.
    """
    parser = argparse.ArgumentParser(prog="appvault",
                                     description="Interface with Appvault")
    runmode_group = parser.add_mutually_exclusive_group()
    runmode_group.add_argument("-e", "--encrypt", action="store_true",
                               help=("Encryption mode (encrypt infile and "
                                     "store in outfile (if supplied))"))
    runmode_group.add_argument("-r", "--run", action="store_true",
                               help=("Run mode (run encrypted infile). "
                                     "Default mode."))
    parser.add_argument("-o", "--outfile", type=Path,
                        help="File that encrypted data should be written to")
    parser.add_argument("infile", type=Path,
                        help=("File name to use (file to encrypt if "
                              "--encrypt, else file to run"))

    args = parser.parse_args()

    if args.encrypt:
        print("encrypting")
        if args.outfile is None:
            args.outfile = Path(f"{args.infile}.secure")
        encrypt(args.infile, args.outfile)
    else:
        print("running")
        run(args.infile)


if __name__ == "__main__":
    main()
