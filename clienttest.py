from client import appvault
from pathlib import Path
import os

if os.path.isfile("demo_script0.py.secure"):
    os.remove("demo_script0.py.secure")
print("Grabbing communicator...")
comms = appvault.Communicator()
print("Grabbed communicator")
print("Encrypting file...")
appvault.encrypt(Path("demo_script0.py"),
                 Path("demo_script0.py.secure"),
                 comms)
print("Encrypted file.\nExecuting encrypted file...")
appvault.run(Path("demo_script0.py.secure"), comms)
print("Done executing encrypted file")
