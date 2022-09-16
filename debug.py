import numpy as np
import serial, time
utf_array = ["aa", "0x23"]

port = 'COM3'
baud_rate = 9600
address = 0
voltage_offset=0.02

sp = serial.Serial(port, baud_rate, timeout=2)

value = 1
num_bytes = 1
length_packet = 26

def makeStack(byte_address, byte_value):

    start = ['0xaa', '0x00', byte_address]
    val = []
    val.append(str(hex(byte_value)))
    reserved = ["0x00" for i in range(0, 21)]
    print("val:", val)

    before_checksum = np.concatenate((start, val, reserved), axis=0)

    checksum = CalculateChecksum(before_checksum)
    checksum_str = str(hex(checksum))

    command = np.concatenate((before_checksum, [checksum_str.encode()]), axis=0)
    print("Stack: ", command, len(command))

    # command_utf8 = "\\".join(command).encode("utf-8")
    # print(command_utf8)

    command_int = [int(comi, 16) for comi in command]
    # print(command_int, len(command_int))

    # print(bytearray(command_int))
    return bytearray(command_int)

def CalculateChecksum(cmd):
    '''Return the sum of the bytes in cmd modulo 256.
    '''
    # print(len(cmd))
    assert((len(cmd) == length_packet - 1) or (len(cmd) == length_packet))
    checksum = 0
    for i in range(length_packet - 1):
        # print(cmd[i], "  ", int.from_bytes(cmd[i], "big") )
        checksum +=  int(cmd[i],16)
    checksum %= 256
    return checksum

# Set to remote control
message = "Set control to local"
bytes_written = sp.write(makeStack("0x20", 1))
response = sp.read(length_packet)
print(f"{message}: {hex(response[3])}\n")

# Set voltage to zero
message = "Set voltage to zero"
bytes_written = sp.write(makeStack("0x23", 0))
response = sp.read(length_packet)
print(f"{message}: {hex(response[3])}\n")

# Set to local control
message = "Set control to local"
bytes_written = sp.write(makeStack("0x20", 0))
response = sp.read(length_packet)
print(f"{message}: {hex(response[3])}\n")