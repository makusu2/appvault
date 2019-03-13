import sys
import nacl.secret
import nacl.utils

if sys.argv[1] not in ["encrypt", "decrypt"]:
    raise ValueError("First argument to must be 'encrypt' or 'decrypt'")

key = b'0'*32
box = nacl.secret.SecretBox(key)
encrypting = sys.argv[1] == "encrypt"
filename_given = sys.argv[2]

if encrypting:
    filename_unencrypted = sys.argv[2]
    filename_encrypted = f"{filename_unencrypted}.secure"

    with open(filename_unencrypted, 'rb') as unencrypted_file, \
            open(filename_encrypted, 'wb') as encrypted_file:
        unencrypted_data = unencrypted_file.read()
        encrypted_data = box.encrypt(unencrypted_data)
        encrypted_file.write(encrypted_data)
else:
    filename_encrypted = sys.argv[2]
    filename_decrypted = f"{filename_encrypted}.unsecured"
    with open(filename_encrypted, 'rb') as encrypted_file, \
            open(filename_decrypted, 'wb') as decrypted_file:
        encrypted_data = encrypted_file.read()
        decrypted_data = box.decrypt(encrypted_data)
        decrypted_file.write(decrypted_data)
