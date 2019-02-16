"""
This module represents the coprocessor.
It should be executed on the raspberry pi.
It will return a bytestring representing the combined stdout/stderr (although these can be separated later).
"""


import subprocess
import os

def wait_for_data() -> bytes:
    """
    In the future this will receive data from serial communication.
    For now, it will just use the data from securedbin.sexe.
    """
    with open('securedbin.sexe','rb') as f:
        return  f.read()
def execute_data(encrypted_data:bytes):
    """
    1. Decrypt the data and execute as much of it as possible.
        We can execute it all now, but later it might ask for input which we'll have to wait for.
    2. Once the data finishes executing, return its return value.
        For most programs this is the "success value", but the sample should return 12345.
    
    """
    decrypted_data = bytes([(data_byte-1)%256 for data_byte in encrypted_data])
    with open('temp.exe','wb') as f_out:
        f_out.write(decrypted_data)
    command_result = subprocess.run('./temp.exe',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    os.remove('temp.exe')
    return "Error(s):\n{}\n\nOutput:\n{}".format(command_result.stderr,command_result.stdout)
    
if __name__=="__main__":
    encrypted_data = wait_for_data()
    result = execute_data(encrypted_data)
    print("Result:\n{}".format(result)) #We would be returning it here (stdout separately from stderr) later.