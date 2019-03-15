from io import BytesIO
import serial
import re
from serial.tools import list_ports


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


print("Getting comport...")
SER = get_comport()
print("Got comport")


def recv_task():
    """Returns a tuple of (task_bytes, identifier)"""
    start_line = SER.readline()
    if not start_line:
        return None, None
    try:
        identifier = re.match(rb"000START000(...)\n", start_line).group(1)
    except AttributeError:
        print(f"start_line was {start_line}")
        raise
    next_line = SER.readline()
    task_bytes = b""
    while not next_line.endswith(b"000END000\n"):
        task_bytes += next_line
        next_line = SER.readline()
    task_bytes += next_line.replace(b"000END000\n", b"")
    return task_bytes, identifier


def send(message: bytes):
    SER.write(message)


class SerialWriter:
    def __init__(self, identifier):
        self.buffer = BytesIO()
        self.identifier = identifier

    def write(self, msg):
        if isinstance(msg, str):
            msg = msg.encode()
        self.buffer.write(msg)

    def flush(self):
        buffer_val = self.buffer.getvalue()
        send(b"000START000" + self.identifier + b"\n" + buffer_val
             + b"000END000\n")
        self.buffer = BytesIO()


SERIAL_OUT = SerialWriter(b"out")
SERIAL_ERR = SerialWriter(b"err")
SERIAL_RES = SerialWriter(b"res")
