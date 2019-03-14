from . import comms


def run(infile):
    with open(infile, "rb") as infile_open:
        encrypted_data = infile_open.read()
        comms.request_run(encrypted_data)
