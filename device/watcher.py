"""
Main monitor methods for Appvault device; keep checking for new data and act
Spinning cursor: https://stackoverflow.com/questions/4995733/
"""


import sys
import nacl.secret
import nacl.utils
import asteval
from . import comms
from .comms import SERIAL_OUT, SERIAL_ERR, SERIAL_RES
import time
import itertools



key = b'0'*32  # this will be changed when we have the actual key
box = nacl.secret.SecretBox(key)
spinner = itertools.cycle("-/|\\")

def run_and_send(encrypted_data):
    decrypted_data = box.decrypt(encrypted_data)
    eval_interpreter = asteval.Interpreter(writer=SERIAL_OUT,
                                           err_writer=SERIAL_ERR)
    result = eval_interpreter(decrypted_data)
    SERIAL_RES.write(str(result).encode())
    for gateway in [SERIAL_OUT, SERIAL_ERR, SERIAL_RES]:
        gateway.flush()


def encrypt_and_send(program_data):
    encrypted_data = box.encrypt(program_data)
    comms.send(b"000START000enc\n" + encrypted_data + b"000END000\n")


def keep_checking():
    sys.stdout.write(next(spinner))
    sys.stdout.flush()
    while True:
        task_bytes, task_identifier = comms.recv_task()
        if task_identifier == b"enr":
            sys.stdout.write(f"\b")
            #sys.stdout.flush()
            print("Got encryption request")
            encrypt_and_send(task_bytes)
            print("Completed encryption request")
        elif task_identifier == b"run":
            sys.stdout.write(f"\b")
            #sys.stdout.flush()
            print("Got run request")
            run_and_send(task_bytes)
            print("Completed run request")
        elif task_identifier is None:
            sys.stdout.write(f"\b{next(spinner)}")
            sys.stdout.flush()
            #print(next(spinner))
            continue
        else:
            raise ValueError(f"task_identifier {task_identifier} not "
                             "one of ['enr', 'run']")
