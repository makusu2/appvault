import sys
import nacl.secret
import nacl.utils


def decrypt(filename_encrypted):
    filename_encrypted = sys.argv[2]
    filename_decrypted = f"{filename_encrypted}.unsecured"
    with open(filename_encrypted, 'rb') as encrypted_file, \
            open(filename_decrypted, 'wb') as decrypted_file:
        encrypted_data = encrypted_file.read()
        decrypted_data = box.decrypt(encrypted_data)
        decrypted_file.write(decrypted_data)


def encrypt(filename_unencrypted):
    filename_unencrypted = sys.argv[2]
    filename_encrypted = f"{filename_unencrypted}.secure"

    with open(filename_unencrypted, 'rb') as unencrypted_file, \
            open(filename_encrypted, 'wb') as encrypted_file:
        unencrypted_data = unencrypted_file.read()
        encrypted_data = box.encrypt(unencrypted_data)
        encrypted_file.write(encrypted_data)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError("Usage: crypt.py <encrypt, decrypt> <filename>")
    if sys.argv[1] not in ["encrypt", "decrypt"]:
        raise ValueError("First argument to must be 'encrypt' or 'decrypt'")

    key = b'0'*32 # this will be changed when we have the actual key
    box = nacl.secret.SecretBox(key)

    if sys.argv[1] == "encrypt":
        encrypt(sys.argv[2])
    else:
        decrypt(sys.argv[2])
