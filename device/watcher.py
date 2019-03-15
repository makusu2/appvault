import nacl.secret
import nacl.utils
import asteval
from . import comms
from .comms import SERIAL_OUT, SERIAL_ERR, SERIAL_RES
import time


key = b'0'*32  # this will be changed when we have the actual key
box = nacl.secret.SecretBox(key)


def run_and_send(encrypted_data):
    decrypted_data = box.decrypt(encrypted_data)
    eval_interpreter = asteval.Interpreter(writer=SERIAL_OUT,
                                           err_writer=SERIAL_ERR)
    result = eval_interpreter(decrypted_data)
    SERIAL_RES.write(str(result).encode())
    for gateway in [SERIAL_OUT, SERIAL_ERR, SERIAL_RES]:
        #gateway.write(b"\n")
        gateway.flush()


def encrypt_and_send(program_data):
    encrypted_data = box.encrypt(program_data)
    comms.send(b"000START000enc\n" + encrypted_data + b"000END000\n")


def keep_checking():
    while True:
        task_bytes, task_identifier = comms.recv_task()
        if task_identifier == b"enr":
            print("Got encryption request")
            encrypt_and_send(task_bytes)
            print("Completed encryption request")
        elif task_identifier == b"run":
            print("Got run request")
            run_and_send(task_bytes)
            print("Completed run request")
        elif task_identifier is None:
            #print("No data received, continuing...")
            continue
        else:
            raise ValueError(f"task_identifier {task_identifier} not "
                             "one of ['enr', 'run']")
