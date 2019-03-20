# -*- coding: utf-8 -*-
"""
Serial communication functions for the Appvault client program.

"""
import sys
import serial
from serial.tools import list_ports


SOH = b'\x01'
STX = b'\x02'
ETX = b'\x03'
EOT = b'\x04'


def as_packet(id, text):
    if isinstance(id, str):
        id = id.encode()
    if isinstance(text, str):
        text = text.encode()
    assert len(id) == 3, f"ID: {id}"
    size = len(text)
    size_as_bytes = bytes([255]*(size//255) + [size % 255] + [0])
    return SOH + id + size_as_bytes + text + ETX + EOT


def read_id_and_bytes(port):
    soh_bytes = port.read()
    if not soh_bytes:
        return None, None
    assert soh_bytes == SOH, f"soh_bytes: {soh_bytes}"
    identifier = port.read_until(size=3)
    transmission_size = sum(port.read_until(bytes([0])))
    task_bytes = port.read_until(size=transmission_size)
    etx_bytes = port.read()
    assert etx_bytes == ETX, f"Expected {ETX}: {etx_bytes}"
    eot_bytes = port.read()
    assert eot_bytes == EOT, f"Expected {EOT}: {eot_bytes}"
    return identifier, task_bytes


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
    if len(comports) > 1:
        chosen_port = get_selection([comport[0] for comport in comports],
                                    ("Multiple comports detected; please "
                                     "enter comport to use."))
    else:
        chosen_port = comports[0][0]
    try:
        return serial.Serial(chosen_port, timeout=1, exclusive=True)
    except serial.serialutil.SerialException:
        print("Error: Could not open port. Maybe it's already in use?")
        return get_comport()


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

        Raises
        -------
        TimeoutError
            More data was expected in response from the device but not
            received in time.

        Returns
        --------
        :class:`bytes`
            The encrypted version of the input bytes.
        """
        self.port.write(as_packet(b"enr", data))
        identifier, encrypted_bytes = read_id_and_bytes(self.port)
        assert identifier == b"enc", f"Identifier was {identifier}"
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
        self.port.write(as_packet(b"run", data))
        while True:
            identifier, output_bytes = read_id_and_bytes(self.port)
            if identifier == b"out":
                sys.stdout.write(output_bytes.decode())
            elif identifier == b"err":
                sys.stderr.write(output_bytes.decode())
            elif identifier == b"res":
                return output_bytes.decode()
            elif identifier is None:
                raise TimeoutError("Nothing received")
            else:
                raise ValueError(f"ID {identifier}, data {output_bytes}")
