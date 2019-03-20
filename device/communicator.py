from io import BytesIO
import re
import serial
from serial.tools import list_ports


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

    def recv_task(self):
        """Returns a tuple of (task_bytes, identifier)"""
        start_line = self.port.readline()
        if not start_line:
            return None, None
        try:
            identifier = re.match(rb"000START000(...)\n", start_line).group(1)
        except AttributeError:
            print(f"start_line was {start_line}")
            raise
        next_line = self.port.readline()
        task_bytes = b""
        while not next_line.endswith(b"000END000\n"):
            task_bytes += next_line
            next_line = self.port.readline()
        task_bytes += next_line.replace(b"000END000\n", b"")
        return task_bytes, identifier


class SerialWriter:
    """Represents the serial capture writers for stdout, stderr, and result

    Attributes
    -----------
    comms: :class:`Communicator`
        The serial communicator for data transmissions
    buffer: :class:`BytesIO`
        The buffer in which written bytes are stored until flush.
        This is remade after each flush so do not save it in a variable.
    identifier: :class:`str`
        The identifier for the data. Should be one of ['out', 'err', 'res'].
    """
    def __init__(self, comms, identifier):
        self.comms = comms
        self.buffer = BytesIO()
        self.identifier = identifier

    def write(self, msg):
        """Write capture method. Adds to current buffer."""
        if isinstance(msg, str):
            msg = msg.encode()
        self.buffer.write(msg)

    def flush(self):
        """Sends stored data and remakes buffer."""
        buffer_val = self.buffer.getvalue()
        self.comms.port.write(b"000START000" + self.identifier + b"\n"
                              + buffer_val + b"000END000\n")
        self.buffer = BytesIO()
