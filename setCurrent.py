'''
This code looks relies on Linux kernel's generic drivers
for serial connections. It looks for the Prolific USB-serial 
converter shipped with the BK Precision 1787-B, 
grants access to the user, 
then sets the voltage output. 

Please read the manual to learn more about the encoding 
of the words sent through serial to the equipment.

Luan Koerich, Nov 2022.
'''

import numpy as np, serial, time, sys, platform
import serial.tools.list_ports
from pyPS import *

def main():

    # Test for the right number of arguments
    if len(sys.argv) != 2:
        print("\nPlease provide a single value in volts.\nTo set the voltage output to 15.55 V, use:\npython setVoltage.py 15.55")
        sys.exit(1)

    # Required parameters
    baud_rate = 9600
    current = float(sys.argv[1])
    ON = 1
    OFF = 0

    # Send values to the PS
    ps = findPS(baud_rate)
    setRemoteControl(ps, ON)
    setCurrentLimit(ps, current)
    time.sleep(1)
    status = readStatus(ps)
    print("Max. current (A):", status["Max. current (A)"])
    print("Measured current output (A):", status["Measured current output (A)"])
    setRemoteControl(ps, OFF)
    ps.close()

main()