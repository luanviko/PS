import numpy as np, serial, time, sys
import serial.tools.list_ports

## Code by Luan Koerich, University of Regina/CA. 
## Please read user manual for more details.

def main():

    # Test for the right number of arguments
    if len(sys.argv) != 2:
        print("\nPlease provide a single value in volts.\nTo set the voltage output to 15.55 V, use:\npython setVoltage.py 15.55")
        sys.exit(1)

    # Required parameters
    baud_rate = 9600
    voltage_offset=0.02
    voltage = float(sys.argv[1])

    # For easier reading
    ON = 1
    OFF = 0

    # Talk to the PS
    ps = findPS(baud_rate)
    setRemoteControl(ps, ON)
    setVoltage(ps, 0., voltage_offset)
    time.sleep(4)
    switchVoltage(ps, ON)
    rampUp(ps, voltage, voltage_offset)
    ps.close()

def findPS(baud_rate, ps_address=0, vtimeout=2):
    ## Look for the any port with Prolific in it.
    ## Assume a single PS connected at a time.
    ports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    for port in ports:
        if ('Prolific' in port[1]):
            print(port[1], "found.")
            port_name = port[0]
        else:
            print("Prolific USB-serial converter not found.")
            sys.exit(2)
    return serial.Serial(port_name, baud_rate, timeout=vtimeout)

def setRemoteControl(ps, ON_OFF, ps_address=0, length_packet=26):
    ## Sets 0x20 to 3rd byte and changes the 4rd byte to ON_OFF.
    bytes_written = ps.write(makeStack("0x20", ON_OFF))
    response = ps.read(length_packet)
    if response:
        if (hex(response[3]) == "0x80") and (ON_OFF==1):
            print(f"Remote control: ON ({hex(response[3])}).")
        elif (hex(response[3]) == "0x80") and (ON_OFF==0):
            print(f"Remote control: OFF ({hex(response[3])}).")
        else:
            print(f"Remote control on/off: failed ({hex(response[3])}).")
    else:
        print("Remote control on/off: communication failed.")

def switchVoltage(ps, ON_OFF, ps_address=0, length_packet=26):
    ## Sets 0x21 at 3rd byte and changes 4th byte to ON_OFF.
    bytes_written = ps.write(makeStack("0x21", ON_OFF))
    response = ps.read(length_packet)
    if response:
        if (hex(response[3]) == "0x80") and (ON_OFF==1):
            print(f"Voltage output is now ON ({hex(response[3])}).")
        elif (hex(response[3]) == "0x80") and (ON_OFF==0):
            print(f"Voltage output is now OFF ({hex(response[3])}).")
        else:
            print(f"Turning voltage on/off: failed ({hex(response[3])}).")
    else:
        print("Turning on/off: communication failed.")

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
    if response:
        if (hex(response[3]) == "0x80"):
            print(f"Changed voltage to: {original_voltage} V.")
        else:
            print(f"Changing voltage: failed ({hex(response[3])})")
    else:
        print("Changing voltage: communication failed.")

def checksum256(command):
    ## Mod 256 of the sum of 25 adresses written into command.
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

def rampUp(ps, final_voltage, voltage_offset, initial_voltage=0., step=0.5, wait=1.2):
    ## Go from 0 to a given voltage waiting after every step.
    voltage_range = np.arange(initial_voltage, final_voltage+voltage_offset, step)
    for voltage in voltage_range:
        setVoltage(ps, voltage, voltage_offset)
        time.sleep(wait)

def readVoltage(ps, length_packet=26):
    ## Send an empty stack to 0x26 then decodes the response.
    bytes_written = ps.write(makeStack("0x26", 0))
    response = ps.read(length_packet)
    voltage_digits = [response[8], response[7], response[6], response[5]]
    voltage_digits = [hex(v) for v in voltage_digits]
    pairs = [voltage[2:] for voltage in voltage_digits]
    encoded_voltage = "0x"+"".join(pairs)
    voltage = float(int(encoded_voltage, 16))/1000.
    return voltage

main()