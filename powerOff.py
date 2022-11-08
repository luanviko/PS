'''
This code relies on Linux kernel's generic drivers for serial connections. 
It opens for the Prolific USB-serial converter shipped with the BK Precision 1787-B, 
then sends commands to its memory.

Please read the manual to learn more about the encoding 
of the words sent through serial to the equipment.

Luan Koerich, Nov 2022.
'''

import numpy as np, serial, time, sys, platform
import serial.tools.list_ports
from pyPS import *

def main():

    # Required parameters
    baud_rate = 9600
    voltage_offset=0.02
    ON  = 1
    OFF = 0

    # Communication
    ps = findPS(baud_rate)
    setRemoteControl(ps, ON)
    changeVoltage(ps, voltage_offset, new_voltage=0.)
    switchVoltage(ps, OFF)
    setRemoteControl(ps, OFF)
    ps.close()

main()