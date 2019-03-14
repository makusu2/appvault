import sys
import serial
from serial.tools import list_ports
import time

SER = serial.serial_for_url("loop://", timeout=5)  # get serial port


def request_encryption_bytes(data):
    SER.write(b"000START000enr\n")
    SER.write(data)
    SER.write(b"\n000END000\n")
    # TODO get a better way of finding start/end
    time.sleep(1)
    next_line = SER.readline()
    assert next_line == b"000START000enc\n", f"got {next_line}"
    next_line = SER.readline()
    while not next_line.endswith(b"000END000\n"):
        yield next_line
        next_line = SER.readline()
    yield next_line.replace(b"000END000\n", b"")


def request_run(data):
    SER.write(b"000START000run\n")
    SER.write(data)
    SER.write(b"000END000\n")
    time.sleep(1)
    while True:
        start_line = SER.readline()
        if start_line == b"000START000out\n":
            next_line = SER.readline()
            while next_line != b"000END000\n":
                sys.stdout.write(next_line.decode())
                next_line = SER.readline()
        elif start_line == b"000START000err\n":
            next_line = SER.readline()
            while next_line != b"000END000\n":
                sys.stderr.write(next_line.decode())
                next_line = SER.readline()
        elif start_line == b"000START000res\n":
            sys.stdout.write("\nRESULT:\n")
            next_line = SER.readline()
            while next_line != b"000END000\n":
                sys.stdout.write(next_line.decode())
                next_line = SER.readline()
        elif start_line == b"":
            raise TimeoutError("Nothing received")
        else:
            raise ValueError(f"Start line was {start_line}")
