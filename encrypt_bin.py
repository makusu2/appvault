"""
This module should be used to encrypt a .exe.
Currently it only writes to 'securedbin.sexe' but this can easily be changed.
Currently, it only fake encrypts by adding 1 (modulo 256) to every byte.
If the encryption method is updated, it must also be updated in coprocessor.py.
"""


import sys
file_to_encrypt = sys.argv[1]
with open(file_to_encrypt,'rb') as f:
    unencrypted_data = f.read()
    encrypted_data = bytes([(data_byte+1)%256 for data_byte in unencrypted_data])
    with open('securedbin.sexe','wb') as f_out:
        f_out.write(encrypted_data)