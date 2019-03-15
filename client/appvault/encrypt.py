from . import comms


def encrypt(infile, outfile):
    with open(infile, "rb") as infile_open, \
            open(outfile, "wb") as outfile_open:
        unencrypted_data = infile_open.read()
        encrypted_bytes = comms.request_encryption_bytes(unencrypted_data)
        outfile_open.write(encrypted_bytes)
