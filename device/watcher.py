"""
Main monitor methods for Appvault device; keep checking for new data and act
Spinning cursor: https://stackoverflow.com/questions/4995733/
"""


import sys
import itertools
import nacl.secret
import nacl.utils
import asteval
from .communicator import (Communicator, SerialWriter,
                           as_packet, read_id_and_bytes)


SPINNER = itertools.cycle("-/|\\")


class Watcher:
    def __init__(self, key=b'0'*32):
        self.box = nacl.secret.SecretBox(key)
        self.comms = Communicator()
        self.serial_out = SerialWriter(self.comms, b"out")
        self.serial_err = SerialWriter(self.comms, b"err")
        self.serial_res = SerialWriter(self.comms, b"res")

    def run_and_send(self, encrypted_data):
        """Runs encrypted data and prints results to serial out/err/res."""
        decrypted_data = self.box.decrypt(encrypted_data)
        eval_interpreter = asteval.Interpreter(writer=self.serial_out,
                                               err_writer=self.serial_err)
        result = eval_interpreter(decrypted_data)
        self.serial_res.write(str(result).encode())
        for gateway in [self.serial_out, self.serial_err, self.serial_res]:
            gateway.flush()

    def encrypt_and_send(self, program_data):
        """Encrypts data and sends encrypted result over comms."""
        encrypted_data = self.box.encrypt(program_data)
        self.comms.port.write(as_packet(b"enc", encrypted_data))

    def keep_checking(self):
        """Keep checking for new data and act accordingly."""
        sys.stdout.write(next(SPINNER))
        sys.stdout.flush()
        while True:
            task_identifier, task_bytes = self.comms.recv_task()
            if task_identifier == b"enr":
                sys.stdout.write("\b")
                print("Got encryption request")
                self.encrypt_and_send(task_bytes)
                print("Completed encryption request")
            elif task_identifier == b"run":
                sys.stdout.write("\b")
                print("Got run request")
                self.run_and_send(task_bytes)
                print("Completed run request")
            elif task_identifier is None:
                sys.stdout.write(f"\b{next(SPINNER)}")
                sys.stdout.flush()
                continue
            else:
                raise ValueError(f"task_identifier {task_identifier} not "
                                 "one of ['enr', 'run']")
