#!/bin/bash

echo "Searching for Prolific USB-serial converter at /dev/tty*:"
for syspath in $(find /dev/tty*); do
    (
        stringtest="$(udevadm info -q property --export $syspath | grep Prolific)"

        if [ -z "$stringtest" ]
        then
            echo "   Prolific USB-serial converter not found at: $syspath"
        else
            echo "   Prolific USB-serial converter found at: $syspath..."
            while true; do
            read -p "   Do you want to grant "$USER" access to it?" yn
                case $yn in
                    [Yy]* ) sudo setfacl -m u:$USER:rw- $syspath; echo $syspath > ./deviceSysPath.config; break;;
                    [Nn]* ) exit;;
                    * ) echo "Please answer y or n.";;
                esac
            done
        fi
    )
done