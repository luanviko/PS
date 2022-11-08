import numpy as np, serial, time, sys, platform
import serial.tools.list_ports
from pyPS import *

def main():

    # Required parameters
    baud_rate = 9600

    # Send values to the PS
    ps = findPS(baud_rate)
    printStatus(ps)
    ps.close()

main()