import numpy as np
import serial, time, sys
utf_array = ["aa", "0x23"]

def main():
    ## Looks for a PS and sets the voltage to sys.argv[1].

    if len(sys.argv) != 2:
        print("\nPlease provide a single value in volts.\nTo set the voltage output to 15.55 V, use:\npython setVoltage.py 15.55")
        sys.exit(1)

    baud_rate = 9600
    voltage_offset=0.02
    voltage = float(sys.argv[1])

    ON = 1
    OFF = 0

    ps = findPS(baud_rate)
    turnVoltage(ps, OFF)
    

def findPS(baud_rate, ps_address=0, vtimeout=2):
    ## Look for the any port with Prolific in it.
    ## Assume a single PS connected at a time.
    ps = serial.Serial("COM3", baud_rate, timeout=vtimeout)
    return ps

def turnVoltage(ps, ON_OFF, ps_address=0, length_packet=26):
    bytes_written = ps.write(makeStack("0x21", ON_OFF))
    response = ps.read(length_packet)
    print("Remote control:", hex(response[3]))

def setVoltage(ps,  a, voltage_offset, length_packet=26):

    print("HHHEHEHEHER:", length_packet)
    original_voltage = a
    a = float(a)+voltage_offset
    print(a)
    a = np.int(a*1000)
    print(a, hex(a))
    a = hex(a)
 
    if len(a) > 0:
        if (len(a) % 2 == 0):
            pairs = ["0x"+a[i:i+2] for i in range(2, len(a), 2)]
            pairs = np.flip(pairs, axis=None)
        else:
            a = "0x0"+a[2:]
            pairs = ["0x"+a[i:i+2] for i in range(2, len(a), 2)]
            pairs = np.flip(pairs, axis=None)
    
    bytes_written = ps.write(makeStack3(ps_address, "0x23", pairs))
    response = ps.read(length_packet)

    print("Voltage: ", original_voltage, a, pairs)
    print("Voltage control:", hex(response[3]), "\n")

def checksum256(command):
    command_int = [int(comi, 16) for comi in command]
    return np.sum(command_int) % 256

def makeStack(byte_address, byte_value, length_packet=26, ps_address=0):

    start = ['0xaa', str(hex(ps_address)), byte_address]
    val = []
    val.append(str(hex(byte_value)))
    reserved = ["0x00" for i in range(0, 21)]
    # print("val:", val)

    before_checksum = np.concatenate((start, val, reserved), axis=0)

    checksum = checksum256(before_checksum)
    checksum_str = str(hex(checksum))

    command = np.concatenate((before_checksum, [checksum_str.encode()]), axis=0)
    # print("Stack: ", command, len(command))

    command_int = [int(comi, 16) for comi in command]

    return bytearray(command_int)

main()