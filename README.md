# PS

This is a set of scripts and functions 
to set the voltage and current outputs of the 
BK Precision 1787B DC power supply (PS).

Since electronic boards require a slow increase 
of the high voltage (HV) supply, 
these scripts will "ramp up" the voltage output 
from zero to the final operating voltage.

The PS is shipped with a IT-E132B serial-to-USB adapter. 
To communicate with the PS, 
I use `pyserial`, as suggested by the manufacturer. 
You can find the manufacturer's own software [on their offical page](https://www.bkprecision.com/products/power-supplies/1787B-0-72vdc-0-15a-programmable-dc-supply-w-rs232-interface.html). 

This software is not based on the manufacter's API, 
but uses the information available on the power supply manual.


## Dependencies

The script was developed using `python 3.10.6`, `pyserial 3.5` and `numpy 1.23.3`. Use `pip` to install the packages, that is, 
```bash
pip3 install -U pyserial numpy
```

This script was developed and tested under Windows 10 and Ubuntu 22.04.
Under Windows, you have to install the drivers provided 
by the manufacturer, [found here](https://www.bkprecision.com/products/power-supplies/1787B-0-72vdc-0-15a-programmable-dc-supply-w-rs232-interface.html). 
On Linux, the generic serial drivers suffice. 


## Using this library on Linux

### Set up 
You can use the `findPS.sh` to find the `/dev/` directory 
of the power supply.

```bash
git clone https://github.com/luanviko/PS
mv ./PS
chmod u+x ./findPS.sh
./findPS.sh
```
You will have to run `./findPS.sh` any time you restart your computer or log out, because you need privileges to access system path of USB
connections under Linux.

### Print status
Decodes the bytes written on the memory 
and adds them to a dictionary. 
This disctionary may be added to MIDAS in the future.
To use it, move into the PS folder and 
```bash
python3 getStatus.py
```
It should print lines like these
```bash
The following was decoded from the power supply stack:
  Power output: ON
  Voltage setting (V): 73.0
  Measured current output (A): 0.0
  Measured voltage output (V): 0.0
  Max. current (A): 0.02
  Max. voltage (V): 73.0
```

### Set max current (0 - 1.55V)

Move into the PS folder, then 
```bash 
python3 setCurrent.py 0.75
```
to set the maximum current output to 0.75 A.

### Set max. voltage (0 - 73V)

Move into PS folder, then 
```
python3 setMaxVoltage.py 20.52
```
to set the max. voltage output to 20.52 V. 
You may choose any value between 0 and 73.00 V. 

### Set output voltage (0 - max. voltage)

IMPORTANT: It will automatically turn ON the voltage output.
Move into the PS folder, then 
```bash
python3 setVoltage.py 15.55 
```
to set the output voltage to 15.55 V, for example.
Notice that you the maximum output is the max. voltage 
value set with `SetMaxVoltage.py`.

### Power off (set output to 0 V)
IMPORTANT: The output is NOT ZERO until __OFF__
appears on the screen or on the status.
Gradually decrease voltage output to zero
then set it to __OFF__.
From the PS folder, 
```bash
python3 powerOff.py
```

### Experimental: monitor
The `startMonitor.py` will show the status lines 
on the screen and automatically update it every 0.85 s.
Do not use at simultaneously with any of the above scripts.
It is meant to monitor changes on the output voltage 
and current by manual operation of the power supply.


<!-- ## Encoding the voltage value

To send the correct value of HV, 
you need the bytes on addresses 3 to 25.
The encoding of the HV value is in the little-endian manner.
If you want to supply 1.5V, for example, 
you first convert such value to mV, 
then to the hexadecimal base: 15000 ->  -->

