from . import comms


def encrypt(infile, outfile):
    with open(infile, "rb") as infile_open, \
            open(outfile, "wb") as outfile_open:
        unencrypted_data = infile_open.read()
        byte_generator = comms.request_encryption_bytes(unencrypted_data)
        for encrypted_bytes in byte_generator:
            print("Writing ", encrypted_bytes)
            outfile_open.write(encrypted_bytes)
