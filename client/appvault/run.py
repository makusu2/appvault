from . import comms


def run(infile):
    with open(infile, "rb") as infile_open:
        encrypted_data = infile_open.read()
        result = comms.request_run(encrypted_data)
        print("Result: ",result)
