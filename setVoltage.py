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
    setRemoteControl(ps, ON)
    switchVoltage(ps, ON)
    setVoltage(ps, voltage, voltage_offset)
    ps.close()

def findPS(baud_rate, ps_address=0, vtimeout=2):
    ## Look for the any port with Prolific in it.
    ## Assume a single PS connected at a time.
    ps = serial.Serial("COM3", baud_rate, timeout=vtimeout)
    return ps

def setRemoteControl(ps, ON_OFF, ps_address=0, length_packet=26):
    ## Sets 0x20 to 3rd byte and changes the 4rd byte to ON_OFF.
    bytes_written = ps.write(makeStack("0x20", ON_OFF))
    response = ps.read(length_packet)
    if ON_OFF == 1:
        print(f"Remote control: ON ({hex(response[3])})")
    else:
        print(f"Remote control: OFF ({hex(response[3])})")

def switchVoltage(ps, ON_OFF, ps_address=0, length_packet=26):
    ## Sets 0x21 at 3rd byte and changes 4th byte to ON_OFF.
    bytes_written = ps.write(makeStack("0x21", ON_OFF))
    response = ps.read(length_packet)
    print("Voltage output:", hex(response[3]))

def setVoltage(ps, voltage, voltage_offset, length_packet=26):
    ## Encode float into 4 byte addresses using the little-endian manner.
    original_voltage = voltage
    voltage = float(voltage)+voltage_offset
    voltage = np.int(voltage*1000)
    voltage = hex(voltage)
    if len(voltage) > 0:
        if (len(voltage) % 2 == 0):
            pairs = ["0x"+voltage[i:i+2] for i in range(2, len(voltage), 2)]
            pairs = np.flip(pairs, axis=None)
        else:
            voltage = "0x0"+voltage[2:]
            pairs = ["0x"+voltage[i:i+2] for i in range(2, len(voltage), 2)]
            pairs = np.flip(pairs, axis=None)
    ## Send encoded command to _makeStack_ and into the PS. 
    bytes_written = ps.write(makeStack("0x23", pairs))
    response = ps.read(length_packet)
    print("Voltage (V): ", original_voltage, f"({hex(response[3])})")

def checksum256(command):
    ## Mod 256 of the 25 bytes written into command.
    command_int = [int(comi, 16) for comi in command]
    return np.sum(command_int) % 256

def makeStack(byte_address, byte_values, length_packet=26, ps_address=0):
    ## Construct and encode a command using bytearray.
    if isinstance(byte_values, int):
        values = [byte_values]
    else: 
        values = byte_values
    start = ['0xaa', str(hex(ps_address)), byte_address]
    reserved = ["0x00" for i in range(0, 22-len(values))]
    before_checksum = np.concatenate((start, values, reserved), axis=0)
    checksum = checksum256(before_checksum)
    checksum_str = str(hex(checksum))
    command = np.concatenate((before_checksum, [checksum_str.encode()]), axis=0)
    command_int = [int(comi, 16) for comi in command]
    return bytearray(command_int)

main()