#!/bin/bash

# Create a fresh 'available.txt' file
> available.txt
function PING
{   
    # Ping 3 times and suppress internal ping echoes - including errors
    ping -c 3 $1 1> /dev/null 2>&1
    # if exit code of previous ping 0, then
    if [ $? -eq 0 ]
        then
            # Include this IP as one of "available" ones
            echo $1 >> available.txt
    fi
}
# For all addresses inputted, ping them
for address in $@; do
    PING $address &
done

# Need to wait for all child processes to finish
# So that 'connect.py' will read a non-empty file
# See "help wait" for details
wait