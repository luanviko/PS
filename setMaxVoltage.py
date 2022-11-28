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
    voltage = float(sys.argv[1])

    # For easier reading
    ON = 1
    OFF = 0

    # Talk to the PS
    ps = findPS(baud_rate)
    setRemoteControl(ps, ON)
    setMaxVoltage(ps, voltage, voltage_offset=0.)
    setRemoteControl(ps, OFF)
    ps.close()

main()