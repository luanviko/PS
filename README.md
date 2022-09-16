# PS
This is a script to set the voltage output of the BK Precision 1787B DC power supply (PS).
Since electronic boards require a slow increase of the high voltage (HV) supply, 
this script will "ramp up" the voltage output from zero to the final operating voltage.
You can adjust the voltage increase of each step and the time to wait after each increase. 

The PS is shipped with a IT-E132B serial-to-USB adapter. To communicate with the PS, 
we use pyserial, as suggested by the manufacturer. 
You can find the manufacturer's own software [on their offical page](https://www.bkprecision.com/products/power-supplies/1787B-0-72vdc-0-15a-programmable-dc-supply-w-rs232-interface.html). 

## Dependencies
This script was developed and tested under Windows 11 and 10. It requires python >3, pyserial 3.5.
You need to install the appropriate drivers, [found here](https://www.bkprecision.com/products/power-supplies/1787B-0-72vdc-0-15a-programmable-dc-supply-w-rs232-interface.html). 

## Encoding the voltage value

To send the correct value of HV, 
you need the bytes on addresses 3 to 25.
The encoding of the HV value is in the little-endian manner.
If you want to supply 1.5V, for example, 
you first convert such value to mV, 
then to the hexadecimal base: 15000 -> 

