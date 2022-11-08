'''
With these functions you can open the Prolific USB-serial
and change the power supply's parameters and read them.

This code relies either on Linux kernel's generic drivers for serial connections
or the manufacturer's own drivers for Windows. 

Please read the manual to learn more about the encoding 
of the words sent through serial to the equipment.

Luan Koerich, Nov 2022.
'''
import numpy as np, serial, time, sys, platform
import serial.tools.list_ports

def changeVoltage(ps, voltage_offset, new_voltage):
    current_voltage = readVoltage(ps)
    if (new_voltage > current_voltage):
        print("Ramping voltage up...")
        rampUp(ps, new_voltage, voltage_offset, initial_voltage=current_voltage)
        time.sleep(3)
        print("Voltage output: {0:4.2f} V".format(readVoltage(ps)))
    elif (new_voltage < current_voltage):
        print("Ramping voltage down...")
        rampDown(ps, voltage_offset, final_voltage=new_voltage)
        time.sleep(3)
        print("Voltage output: {0:4.2f} V".format(readVoltage(ps)))
    else: 
        print("No voltage to be changed. Voltage output: {0:4.2f} V".format(readVoltage(ps)))

def findPS(baud_rate, ps_address=0, vtimeout=2):
    os_name = platform.system()
    if 'Linux' in os_name:
        return serial.Serial("/dev/ttyUSB0", baud_rate, timeout=vtimeout)
    elif 'Windows' in os_name:
        # Look for the any port with Prolific in it.
        # Assume a single PS connected at a time.
        ports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        for port in ports:
            print(port)
            if ('Prolific' in port[1]):
                print(port[1], "found.")
                port_name = port[0]
            else:
                print("Prolific USB-serial converter not found.\nPlease check power, connection or drivers.")
                sys.exit(2)
    elif 'Darwin' in os_name:
        print("This script does not support Mac Os. Please modify `findPS` function.")
        

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

def setCurrentLimit(ps, current, length_packet=26):
    ## Encode float into 4 byte addresses using the little-endian manner.
    original_current = current
    current = float(current)
    current = int(current*1000)
    current = hex(current)
    if len(current) > 0:
        if (len(current) % 2 == 0):
            pairs = ["0x"+current[i:i+2] for i in range(2, len(current), 2)]
            pairs = np.flip(pairs, axis=None)
        else:
            current = "0x0"+current[2:]
            pairs = ["0x"+current[i:i+2] for i in range(2, len(current), 2)]
            pairs = np.flip(pairs, axis=None)
    ## Send encoded command to _makeStack_ and into the PS. 
    bytes_written = ps.write(makeStack("0x24", pairs))
    response = ps.read(length_packet)
    if response:
        if (hex(response[3]) == "0x80"):
            print(f"Changing current to: {original_current:4.2f} A.", end="\n")
        else:
            print(f"Changing current: failed ({hex(response[3])})")
    else:
        print("Changing current: communication failed.")

def setVoltage(ps, voltage, voltage_offset, length_packet=26):
    ## Encode float into 4 byte addresses using the little-endian manner.
    original_voltage = voltage
    voltage = float(voltage)+voltage_offset
    voltage = int(voltage*1000)
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
            print(f"Voltage set to  : {original_voltage:4.2f} V.", end="\r")
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

def rampUp(ps, final_voltage, voltage_offset, initial_voltage=0., step=0.5, wait=0.8):
    ## Go from 0 to a given voltage waiting after every step.
    voltage_range = np.arange(initial_voltage, final_voltage+voltage_offset+step, step)
    # print(initial_voltage, final_voltage, voltage_range)
    for voltage in voltage_range:
        if (voltage < final_voltage):
            setVoltage(ps, voltage, voltage_offset)
            # print(voltage)
            time.sleep(wait)
        elif (voltage >= final_voltage):
            setVoltage(ps, final_voltage, voltage_offset)
            time.sleep(wait)
            # print(final_voltage+voltage_offset)
            break

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

def rampDown(ps, voltage_offset, final_voltage=0., step=0.5, wait=1):
    current_voltage = readVoltage(ps)
    # last_digit = int(str(current_voltage)[-1])
    voltage_range = np.arange(current_voltage, final_voltage+voltage_offset-step, -1.*step)
    for voltage in voltage_range:
        if (voltage > final_voltage):
            setVoltage(ps, voltage, voltage_offset)
            time.sleep(wait)
        elif (voltage <= final_voltage):
            setVoltage(ps, final_voltage, voltage_offset)
            time.sleep(wait)
            break

def decodeBytes(response, positions):
    digits = [response[i] for i in positions]
    digits = [hex(v) for v in digits]
    pairs = [digit[2:] for digit in digits]
    encoded_value = "0x"+"".join(pairs)
    integer_value = int(encoded_value, 16)
    return integer_value

def readStatus(ps, length_packet=26):
    status = {}
    bytes_written = ps.write(makeStack("0x26", 0))
    response = ps.read(length_packet)
    if (int(response[9]) == 128 or int(response[9])==0):
        state = "OFF"
    else: 
        state = "ON"
    status.update({"Power output":state})
    status.update({"Voltage setting (V)":float(decodeBytes(response, [19, 18, 17, 16]))/1000.})
    status.update({"Measured current output (A)":float(decodeBytes(response, [4, 3]))/1000.})
    status.update({"Measured voltage output (V)":float(decodeBytes(response, [8, 7, 6, 5]))/1000.})
    status.update({"Max. current (A)":float(decodeBytes(response, [11, 10]))/1000.})
    status.update({"Max. voltage (V)":float(decodeBytes(response, [15, 14, 13, 12]))/1000.})
    return status

def printStatus(ps):
    status = readStatus(ps)
    print("The following was decoded from the power supply stack:")
    for key in status.keys():
        print(f"  {key}: {status[key]}")

def monitor(ps):
    stop=False
    print("The following was decoded from the power supply stack:")
    while (stop==False):
        status = readStatus(ps)
        line_counts = 0
        update_string = ""
        for key in status.keys():
            line_counts += 1
            update_string += f"  {key}: {status[key]}\n"
        print(update_string, end="\r")
        time.sleep(0.85)
        for i in range(0, line_counts):
            sys.stdout.write("\x1b[1A\x1b[2K") 