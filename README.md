# python-tripplite


Tripp Lite Power Distribution Unit (PDU) control using python script

Written by Jay Schulist <jayschulist@gmail.com>
Version 0.1.1
Date 06/18/2019

./python-tripplite.py -h [hostname] -u [username] -p [password] --[command]
    -h : hostname of the PDU unit to login to
    -u : username to use for login
    -p : Password to use for login
    --[command] : one of the following
        --status
        --cycle=[all|outlet_num]
        --on=[all|outlet_num]
        --off=[all|outlet_num]

Example(s):
    This will print information about the given PDU:
        ./python-tripplite.py -h pdu-e4 -u localadmin -p localadmin --status

    This will cycle all outlets on the given PDU:
        ./python-tripplite.py -h pdu-e4 -u localadmin -p localadmin --cycle=all

    This will power off all outlets on the given PDU:
        ./python-tripplite.py -h pdu-e4 -u localadmin -p localadmin --off=all

    This will power on all outlets on the given PDU:
        ./python-tripplite.py -h pdu-e4 -u localadmin -p localadmin --on=all

