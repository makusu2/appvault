# -*- coding: utf-8 -*-
"""
Serial communication functions for the Appvault client program.

"""


import sys
import serial
from serial.tools import list_ports


def get_selection(choices, query=None):
    """Request user input to choose from a collection of choices.
    If len(choices) == 1, the single choice is returned.

    Parameters
    ----------
    choices: Iterable[:class:`str`]
        An iterable of the choices from which the user must pick.
    query: :class:`str`
        The prompt displayed to the user. Defaults to "Please select one."
    """

    if len(choices) == 1:
        return choices[0]
    query = "Please select one." if query is None else query
    choices_lower = [choice.lower() for choice in choices]
    print(f"{query}\n{choices}")
    response = input()
    try:
        return choices[choices_lower.index(response.lower())]
    except ValueError:
        print("Invalid choice. Please enter a valid choice.")
        return get_selection(choices, query)


def get_comport():
    """Returns a comport after querying the user on which to use.
    If only one valid comport exists, it is returned without alerting the user.

    Raises
    -------
    SystemError
        No valid comports were detected, so none could be chosen.
    """
    comports = list_ports.comports()
    if not comports:
        raise SystemError("No comports detected")
    chosen_port = get_selection([comport[0] for comport in comports],
                                ("Multiple comports detected; please "
                                 "enter comport to use."))
    return serial.Serial(chosen_port, timeout=1)


class Communicator:
    """Represents a serial channel for external communications.

    Attributes
    -----------
    port: :class:`Serial`
        The serial port over which to communicate.

    """

    def __init__(self, port=None):
        self.port = port or get_comport()

    def request_encryption_bytes(self, data: bytes):
        """Sends data to be encrypted on the external device.

        Parameters
        ----------
        data: :class:`bytes`
            The data to be encrypted.

        Returns
        --------
        :class:`bytes`
            The encrypted version of the input bytes.
        """
        encrypted_bytes = b""
        self.port.write(b"000START000enr\n")
        self.port.write(data)
        self.port.write(b"\n000END000\n")
        # TODO get a better way of finding start/end
        next_line = self.port.readline()
        assert next_line == b"000START000enc\n", f"got {next_line}"
        next_line = self.port.readline()
        while not next_line.endswith(b"000END000\n"):
            encrypted_bytes += next_line
            next_line = self.port.readline()
        encrypted_bytes += next_line.replace(b"000END000\n", b"")
        return encrypted_bytes

    def request_run(self, data: bytes):
        """Sends encrypted serial data to be executed on the external device.

        Parameters
        ----------
        data: :class:`bytes`
            The encrypted data to be run.

        Raises
        -------
        TimeoutError
            More data was expected in response from the device but not
            received in time.
        ValueError
            Part of the response from the device does not match expected
            response.

        Returns
        --------
        :class:`bytes`
            The result of the executed program in bytes.
            Cast to bytes is performed by executing str(return_val).encode()
        """

        self.port.write(b"000START000run\n")
        self.port.write(data)
        self.port.write(b"000END000\n")
        while True:
            start_line = self.port.readline()
            if start_line == b"000START000out\n":
                next_line = self.port.readline()
                while not next_line.endswith(b"000END000\n"):
                    sys.stdout.write(next_line.decode())
                    next_line = self.port.readline()
                sys.stdout.write(next_line.decode().replace("000END000\n", ""))
            elif start_line == b"000START000err\n":
                next_line = self.port.readline()
                while not next_line.endswith(b"000END000\n"):
                    sys.stderr.write(next_line.decode())
                    next_line = self.port.readline()
                sys.stderr.write(next_line.decode().replace("000END000\n", ""))
            elif start_line == b"000START000res\n":
                result = ""
                next_line = self.port.readline()
                while not next_line.endswith(b"000END000\n"):
                    result += next_line.decode()
                    next_line = self.port.readline()
                result += next_line.decode().replace("000END000\n", "")
                return result
            elif start_line == b"":
                raise TimeoutError("Nothing received")
            else:
                raise ValueError(f"Start line was {start_line}")
