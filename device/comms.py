from io import BytesIO
import serial
import re


SER = serial.serial_for_url("loop://", timeout=5)  # get serial port


def recv_task():
    """Returns a tuple of (task_bytes, identifier)"""
    start_line = SER.readline()
    if not start_line:
        raise TimeoutError("Nothing received.")
    identifier = re.match(rb"000START000(...)\n", start_line).group(1)
    next_line = SER.readline()
    task_byte_lines = []
    while not next_line.endswith(b"000END000\n"):
        task_byte_lines.append(next_line)
        next_line = SER.readline()
    task_byte_lines.append(next_line.replace(b"000END000\n", b""))
    return b''.join(task_byte_lines), identifier


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
        #assert buffer_val.endswith(b"\n")
        send(b"000START000" + self.identifier + b"\n" + buffer_val
             + b"000END000\n")
        self.buffer = BytesIO()


SERIAL_OUT = SerialWriter(b"out")
SERIAL_ERR = SerialWriter(b"err")
SERIAL_RES = SerialWriter(b"res")
