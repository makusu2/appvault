import argparse
from pathlib import Path
import comms


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interface with Appvault")
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
        with open(args.infile, "rb") as infile_open, \
                open(args.outfile, "wb") as outfile_open:
            unencrypted_data = infile_open.read()
            byte_generator = comms.request_encryption_bytes(unencrypted_data)
            for encrypted_bytes in byte_generator:
                outfile_open.write(encrypted_bytes)
    else:
        print("running")
        with open(args.infile, "rb") as infile_open:
            encrypted_data = infile_open.read()
            comms.request_run(encrypted_data)
