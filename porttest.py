import serial
from serial.tools import list_ports

comports = list_ports.comports()
assert len(comports) == 2

port1 = serial.Serial(comports[0][0], timeout=1)
port2 = serial.Serial(comports[1][0], timeout=1)

port1.write(b"Hi\n")
print("Reading from port2:")
received = port2.readline()
print("Read from port 2: ",received)
