from io import BytesIO
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


def get_selection(choices, query):
    """Request user input to choose from a collection of choices.
    If len(choices) == 1, the single choice is returned.

    Parameters
    ----------
    choices: Iterable[:class:`str`]
        An iterable of the choices from which the user must pick.
    query: :class:`str`
        The prompt displayed to the user. Defaults to "Please select one."
    """
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

    def read_id_and_bytes(self):
        """Returns a tuple of (identifier, task_bytes)"""
        soh_bytes = self.port.read()
        if not soh_bytes:
            return None, None
        assert soh_bytes == SOH, f"soh_bytes: {soh_bytes}"
        identifier = self.port.read_until(size=3)
        transmission_size = sum(self.port.read_until(bytes([0])))
        task_bytes = self.port.read_until(size=transmission_size)
        etx_bytes = self.port.read()
        assert etx_bytes == ETX, f"Expected {ETX}: {etx_bytes}"
        eot_bytes = self.port.read()
        assert eot_bytes == EOT, f"Expected {EOT}: {eot_bytes}"
        return identifier, task_bytes


class SerialWriter:
    """Represents the serial capture writers.
    Best used for stdout, stderr, and result, but works for any identifier.

    Attributes
    -----------
    comms: :class:`Communicator`
        The serial communicator for data transmissions
    buffer: :class:`BytesIO`
        The buffer in which written bytes are stored until flush.
        This is remade after each flush so do not save it in a variable.
    identifier: :class:`str`
        The identifier for the data. Should be one of length 3.
    """
    def __init__(self, comms, identifier):
        self.comms = comms
        self.buffer = BytesIO()
        self.identifier = identifier

    def write(self, msg, also_flush = False):
        """Write capture method. Adds to current buffer."""
        if isinstance(msg, str):
            msg = msg.encode()
        self.buffer.write(msg)
        if also_flush:
            self.flush()

    def flush(self):
        """Sends stored data and remakes buffer."""
        buffer_val = self.buffer.getvalue()
        self.comms.port.write(as_packet(self.identifier, buffer_val))
        self.buffer = BytesIO()
