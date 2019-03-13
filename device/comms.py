from io import StringIO
import serial
import re


SER = None  # get serial port


def recv_task():
    """Returns a tuple of (task_bytes, identifier)"""
    start_line = SER.readline()
    identifier = re.match(rb"000START000(...)\n", start_line).group(1)
    next_line = SER.readline()
    task_byte_lines = []
    while next_line != b"000END000\n":
        task_byte_lines.append(next_line)
        next_line = SER.readline()
    return ''.join(task_byte_lines), identifier


def send(message: bytes):
    print(b"\n\nSending:")
    print(message)
    print(b"\n\n")


class SerialWriter:
    def __init__(self, identifier):
        self.buffer = StringIO()
        self.identifier = identifier

    def write(self, msg):
        self.buffer.write(msg)

    def flush(self):
        buffer_val = self.buffer.getvalue()
        assert buffer_val.endswith("\n")
        send(b"000START000" + self.identifier + b"\n" + buffer_val
             + "000END000\n")
        self.buffer = StringIO()


SERIAL_OUT = SerialWriter("out")
SERIAL_ERR = SerialWriter("err")
SERIAL_RES = SerialWriter("res")
