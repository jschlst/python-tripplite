# python-tripplite

Tripp Lite Power Distribution Unit (PDU) control using python script

Written by Jay Schulist <jayschulist@gmail.com>

Version 0.1.1

Date 06/18/2019


## Example
```
./tripplite.py -h [hostname] {-u [username] -p [password]} --[command]
    -h : hostname of the PDU unit to login
    -u : username to use for login (optional then default used)
    -p : Password to use for login (optional then default used)
    --[command] : one of the following
        --status
        --reboot
        --force
        --cycle=[all|outlet_num]
        --on=[all|outlet_num]
        --off=[all|outlet_num]

Example(s):
    Cycle all outlets on the given PDU using default login credentials:
        python tripplite.py -h pdu-e01 --reboot

    Force a power off, sleep, then power on using default login credentials:
        python tripplite.py -h pdu-e02 --force

    Print information about the given PDU:
        python tripplite.py -h pdu-e04 -u localadmin -p localadmin --status

    Cycle all outlets on the given PDU:
        python tripplite.py -h pdu-e04 -u localadmin -p localadmin --cycle=all

    Power off all outlets on the given PDU:
        python tripplite.py -h pdu-e04 -u localadmin -p localadmin --off=all

    Power on all outlets on the given PDU:
        python tripplite.py -h pdu-e04 -u localadmin -p localadmin --on=all

Log output of command execution located at /tmp/tripplite.log
```

