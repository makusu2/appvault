"""
Execution methods for Appvault client program
"""
import sys
from .communicator import Communicator, SerialWriter


def run(infile, comms=None, return_result=False):
    """Runs an encrypted file on the external Appvault device.

    Parameters
    ----------
    infile: :class:`os.PathLike`
        The name of the encrypted file to be executed.
    comms: Optional[:class:`Communicator`]
        The Communicator to use when transferring and receiving data.
        Defaults to user input.
    return_result: Optional[:class:`bool`]
        If ``True``, return the result of the program, else print the result.

    Raises
    -------
    TimeoutError
        More data was expected in response from the device but not
        received in time.
    ValueError
        Part of the response from the device does not match expected
        response.
    """

    if comms is None:
        comms = Communicator()
    with open(infile, "rb") as infile_open:
        encrypted_data = infile_open.read()
        SerialWriter(comms, b"run").write(encrypted_data, also_flush=True)
        result = None
        while result is None:
            identifier, output_bytes = comms.read_id_and_bytes()
            if identifier == b"out":
                sys.stdout.write(output_bytes.decode())
            elif identifier == b"err":
                sys.stderr.write(output_bytes.decode())
            elif identifier == b"res":
                result = output_bytes.decode()
            elif identifier is None:
                raise TimeoutError("Nothing received")
            else:
                raise ValueError(f"ID {identifier}, data {output_bytes}")
        if return_result:
            return result
        print(f"Result: {result}")
