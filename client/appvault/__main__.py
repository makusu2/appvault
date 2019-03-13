import argparse
from pathlib import Path
import comms


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interface with Appvault")
    parser.add_argument("-e", "--encrypt", help="Encryption mode",
                        action="store_true")
    parser.add_argument("-o", "--outfile", help="Specify outfile", type=Path)
    parser.add_argument("infile", type=Path)
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
