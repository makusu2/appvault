import sys
import serial
from serial.tools import list_ports
import time

def get_selection(choices, query):
    choices_lower = [choice.lower() for choice in choices]
    print(f"{query}\n{choices}")
    response = input()
    try:
        return choices[choices_lower.index(response.lower())]
    except ValueError:
        print("Invalid choice. Please enter a valid choice.")
        return get_selection(choices, query)


def get_comport():
    comports = list_ports.comports()
    if not comports:
        raise SystemError("No comports detected")
    elif len(comports) > 1:
        chosen_port = get_selection([comport[0] for comport in comports],
                                    ("Multiple comports detected; please "
                                     "enter comport to use."))
    else:
        chosen_port = comports[0][0]
    return serial.Serial(chosen_port, timeout=1)


SER = get_comport()


def request_encryption_bytes(data):
    def request_encryption_bytes_gen(data):
        SER.write(b"000START000enr\n")
        SER.write(data)
        SER.write(b"\n000END000\n")
        # TODO get a better way of finding start/end
        next_line = SER.readline()
        assert next_line == b"000START000enc\n", f"got {next_line}"
        encrypted_bytes = next_line = SER.readline()
        while not next_line.endswith(b"000END000\n"):
            yield next_line
            #encrypted_bytes += next_line
            next_line = SER.readline()
        #print("Encrypted bytes: ",encrypted_bytes)
        #return encrypted_bytes + next_line.replace(b"000END000\n", b"")
        yield next_line.replace(b"000END000\n", b"")
    return b''.join(request_encryption_bytes_gen(data))


def request_run(data):
    SER.write(b"000START000run\n")
    SER.write(data)
    SER.write(b"000END000\n")
    while True:
        start_line = SER.readline()
        if start_line == b"000START000out\n":
            next_line = SER.readline()
            while not next_line.endswith(b"000END000\n"):
                sys.stdout.write(next_line.decode())
                next_line = SER.readline()
            sys.stdout.write(next_line.decode().replace("000END000\n", ""))
        elif start_line == b"000START000err\n":
            next_line = SER.readline()
            while not next_line.endswith(b"000END000\n"):
                sys.stderr.write(next_line.decode())
                next_line = SER.readline()
            sys.stderr.write(next_line.decode().replace("000END000\n", ""))
        elif start_line == b"000START000res\n":
            result = ""
            next_line = SER.readline()
            while not next_line.endswith(b"000END000\n"):
                result += next_line.decode()
                next_line = SER.readline()
            result += next_line.decode().replace("000END000\n", "")
            return result
        elif start_line == b"":
            raise TimeoutError("Nothing received")
        else:
            raise ValueError(f"Start line was {start_line}")
