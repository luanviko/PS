'''
With these functions you can open the Prolific USB-serial
and change the power supply's parameters and read them.

This code relies either on Linux kernel's generic drivers for serial connections
or the manufacturer's own drivers for Windows. 

Please read the manual to learn more about the encoding 
of the words sent through serial to the equipment.

Luan Koerich, Nov 2022.
'''
import numpy as np, serial, time, sys, platform, os
import serial.tools.list_ports

def changeVoltage(ps, voltage_offset, new_voltage):
    ''' 
    Determine if voltage is higher than current voltage
    then raise or lower voltage gradually.
    '''
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

def fetchSysPath():
    ''' 
    Open config file containing the system path to the serial port.
    '''
    try:
        with open("./deviceSysPath.config", "r") as file_input: 
            return file_input.readlines()[0].replace("\n","")
    except:
        print("Please try running ./findPS.sh one more time.")
        sys.exit(1)

def findPS(baud_rate, ps_address=0, vtimeout=2):
    os_name = platform.system()
    if 'Linux' in os_name:
        try:
            ps = serial.Serial(fetchSysPath(), baud_rate, timeout=vtimeout)
            return ps 
        except serial.serialutil.SerialException:
            print("Error opening serial port.") 
            sys.stdout.write("Run ./findPS.sh and allow "+os.getlogin()+" to access it.\n")
            sys.exit(1)
        except ValueError:
            print("Error opening serial. Please check baud rate and timeout values.")

    elif 'Windows' in os_name:
        ports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        for port in ports:
            print(port)
            if ('Prolific' in port[1]):
                print(port[1], "found.")
                port_name = port[0]
                return serial.Serial(port[0], baud_rate, timeout=vtimeout)
            else:
                print("Prolific USB-serial converter not found.\nPlease check power, connection or drivers.")
                sys.exit(2)

    elif 'Darwin' in os_name:
        print("This script does not support Mac Os. Please modify `findPS` function.")
        

def setRemoteControl(ps, ON_OFF, ps_address=0, length_packet=26):
    '''
    Set sub address 0x20 to either 1 or 0 (remote or local).
    '''
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
    '''
    Set sub address 0x21 to either 1 or 0 (ON or OFF).
    '''
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

def make_pairs(current):
    ''' 
    Convert decimal value into 4-bit hex pairs
    following little-endian sequence.
    '''
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
    return pairs 

def setCurrentLimit(ps, current, length_packet=26):
    '''
    Encode float into 4 byte addresses using the little-endian manner
    and send it to subaddress 0x24. 
    '''
    bytes_written = ps.write(makeStack("0x24", make_pairs(current)))
    response = ps.read(length_packet)
    if response:
        if (hex(response[3]) == "0x80"):
            print(f"Changing current to: {current:4.2f} A.", end="\n")
        else:
            print(f"Changing current: failed ({hex(response[3])})")
    else:
        print("Changing current: communication failed.")

def setVoltage(ps, voltage, voltage_offset, length_packet=26):
    '''
    Encode float into 4 byte addresses using the little-endian manner
    and send it to subaddress 0x23. 
    '''
    bytes_written = ps.write(makeStack("0x23", make_pairs(voltage)))
    response = ps.read(length_packet)
    if response:
        if (hex(response[3]) == "0x80"):
            print(f"Voltage set to  : {voltage:4.2f} V.", end="\r")
        else:
            print(f"Changing voltage: failed ({hex(response[3])})")
    else:
        print("Changing voltage: communication failed.")

def setMaxVoltage(ps, voltage, voltage_offset, length_packet=26):
    '''
    Encode float into 4 byte addresses using the little-endian manner
    and send it to subaddress 0x22. 
    '''
    bytes_written = ps.write(makeStack("0x22", make_pairs(voltage)))
    response = ps.read(length_packet)
    if response:
        if (hex(response[3]) == "0x80"):
            print(f"Max. voltage set to: {voltage:4.2f} V.", end="\n")
        else:
            print(f"Changing max. voltage: failed ({hex(response[3])})")
    else:
        print("Changing max. voltage: communication failed.")

def checksum256(command):
    '''
    Simple checksum test to be added to the last bit of the stack.
    '''
    command_int = [int(comi, 16) for comi in command]
    return np.sum(command_int) % 256

def makeStack(byte_address, byte_values, length_packet=26, ps_address=0):
    ## Construct and encode a command using bytearray.
    '''
    Build a stack of 26 bits to be sent to the PS. 
    The third bit contains the sub address. 
    The following bits contain the voltage/ current values to be set.
    '''
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
    '''
    Increse voltage gradually from :initial_voltage: to :final_voltage:.
    '''
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
    '''
    Send empty stack to 0x26 and receive status stack.
    Decode bits 8 to 5 in little-endian format
    to convert hex to decimal.
    '''
    bytes_written = ps.write(makeStack("0x26", 0))
    response = ps.read(length_packet)
    voltage_digits = [response[8], response[7], response[6], response[5]]
    voltage_digits = [hex(v) for v in voltage_digits]
    pairs = [voltage[2:] for voltage in voltage_digits]
    encoded_voltage = "0x"+"".join(pairs)
    voltage = float(int(encoded_voltage, 16))/1000.
    return voltage

def rampDown(ps, voltage_offset, final_voltage=0., step=0.5, wait=1):
    '''
    Set voltage to a given value and wait.
    Repeat that until :final_voltage: is reached.
    '''
    current_voltage = readVoltage(ps)
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
    '''
    Follow little-endian format to decode 
    bit pairs into decimal integer value.
    '''
    digits = [response[i] for i in positions]
    digits = [hex(v) for v in digits]
    pairs = [digit[2:] for digit in digits]
    encoded_value = "0x"+"".join(pairs)
    integer_value = int(encoded_value, 16)
    return integer_value

def readStatus(ps, length_packet=26):
    '''
    Send empty stack to 0x26 to get information 
    about the power supply. Decode bytes into decimals 
    and organize into dictionary.
    '''
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
    '''Print status bytes on screen once.'''
    status = readStatus(ps)
    print("The following was decoded from the power supply stack:")
    for key in status.keys():
        if key != "Power output":
            print(f"  {key}: {status[key]:4.2f}")
        else:
            print(f"  {key}: {status[key]}")

def monitor(ps):
    '''Print status on terminal every 0.85 seconds.'''
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