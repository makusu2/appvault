import nacl.secret
import nacl.utils
import asteval
import comms
from comms import SERIAL_OUT, SERIAL_ERR, SERIAL_RES


key = b'0'*32  # this will be changed when we have the actual key
box = nacl.secret.SecretBox(key)


def run_and_send(encrypted_data):
    decrypted_data = box.decrypt(encrypted_data)
    eval_interpreter = asteval.Interpreter(writer=SERIAL_OUT,
                                           err_writer=SERIAL_ERR)
    result = eval_interpreter(decrypted_data)
    SERIAL_RES.write(str(result))


def encrypt_and_send(program_data):
    encrypted_data = box.encrypt(program_data)
    comms.send(b"000START000enc\n" + encrypted_data + b"\n000END000\n")


def main():
    while True:
        task_bytes, task_identifier = comms.recv_task()
        if task_identifier == "enr":
            encrypt_and_send(task_bytes)
        elif task_identifier == "run":
            run_and_send(task_bytes)
        else:
            raise ValueError("task_identifier not one of ['enr', 'run']")


if __name__ == "__main__":
    main()
