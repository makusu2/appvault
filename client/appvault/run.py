"""
Execution methods for Appvault client program
"""


from .communicator import Communicator


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

    """

    if comms is None:
        comms = Communicator()
    with open(infile, "rb") as infile_open:
        encrypted_data = infile_open.read()
        result = comms.request_run(encrypted_data)
        if return_result:
            return result
        print(f"Result: {result}")
