from client import appvault
import device
import threading
from pathlib import Path

device.comms.SER = appvault.comms.SER


threading.Thread(target=device.keep_checking).start()
#appvault.encrypt(Path("demo_script0.py"), Path("demo_script0.py.secure"))
appvault.run(Path("demo_script0.py.secure"))
