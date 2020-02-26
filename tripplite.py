#!/usr/bin/env python

"""
Tripp Lite Power Distribution Unit (PDU) control using python script

Written by Jay Schulist <jayschulist@gmail.com>
Version 0.1.1
Date 06/18/2019

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
"""

import getopt
# import getpass
import os
# import re
import sys
import time

import pexpect


class Tripplite(object):
    COMMAND_PROMPT = '>> '
    COMMAND_TIMEOUT = 100
    LOGFILE = '/tmp/tripplite.log'

    def __init__(self, hostname, username='localadmin', password='localadmin'):
        self.hostname = hostname
        self.username = username
        self.password = password

    def connect(self):
        # Login via telnet (SSH doesn't work with pexpect)
        try:
            self.tel = pexpect.spawn(f'telnet {self.hostname}', encoding='utf-8')
        except:
            raise Exception(f'Unable to connect to PDU {self.hostname}')

        try:
            self.tel.logfile = open(self.LOGFILE, 'w')
            self.tel.expect('^.* login: ', timeout=self.COMMAND_TIMEOUT)
            self.tel.sendline('%s' % self.username)
            self.tel.expect('Password: ', timeout=self.COMMAND_TIMEOUT)
            self.tel.sendline('%s' % self.password)
        except:
            raise Exception('Unable to login')

        # Now at the devices command prompt and ready to run some commands.
        self.tel.expect(self.COMMAND_PROMPT)
        self.tel.sendline('1')

    def status(self):
        self.tel.expect(self.COMMAND_PROMPT, timeout=self.COMMAND_TIMEOUT)
        self.tel.sendline('1')
        self.tel.expect(self.COMMAND_PROMPT, timeout=self.COMMAND_TIMEOUT)
        output_status = self.tel.before[92:-75]
        return output_status

    def cycle(self, port='all'):
        self.tel.expect(self.COMMAND_PROMPT, timeout=self.COMMAND_TIMEOUT)
        self.tel.sendline('3')
        self.tel.expect(self.COMMAND_PROMPT, timeout=self.COMMAND_TIMEOUT)
        self.tel.sendline('6')
        self.tel.expect(self.COMMAND_PROMPT, timeout=self.COMMAND_TIMEOUT)
        self.tel.sendline('Y')
        return True

    def on(self, port='all'):
        self.tel.expect(self.COMMAND_PROMPT, timeout=self.COMMAND_TIMEOUT)
        self.tel.sendline('3')
        self.tel.expect(self.COMMAND_PROMPT, timeout=self.COMMAND_TIMEOUT)
        self.tel.sendline('9')
        self.tel.expect(self.COMMAND_PROMPT, timeout=self.COMMAND_TIMEOUT)
        self.tel.sendline('Y')
        return True

    def off(self, port='all'):
        self.tel.expect(self.COMMAND_PROMPT, timeout=self.COMMAND_TIMEOUT)
        self.tel.sendline('3')
        self.tel.expect(self.COMMAND_PROMPT, timeout=self.COMMAND_TIMEOUT)
        self.tel.sendline('5')
        self.tel.expect(self.COMMAND_PROMPT, timeout=self.COMMAND_TIMEOUT)
        self.tel.sendline('Y')
        return True

    def close(self):
        # Now exit the remote host and close the connection.
        self.tel.sendline('M')
        self.tel.expect(self.COMMAND_PROMPT, timeout=self.COMMAND_TIMEOUT)
        self.tel.sendline('Q')
        self.tel.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __repr__(self):
        return f'PDU connect by telnet to {self.username}@{self.hostname}'


def exit_with_usage():
    print(globals()['__doc__'])
    os._exit(1)


def main():
    force_timeout = 10 * 60

    # Parse the options, arguments
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h:u:p:', ['status', 'cycle=', 'on=', 'off=', 'force', 'reboot'])
    except Exception as e:
        print(str(e))
        exit_with_usage()
    options = dict(optlist)
    if len(args) > 3:
        exit_with_usage()
    # print(options)

    if '-h' in options:
        hostname = options['-h']
    else:
        hostname = input('hostname: ')
    if '-u' in options:
        username = options['-u']
    else:
        username = 'localadmin'
        print(f'Using default username: {username}')
    if '-p' in options:
        password = options['-p']
    else:
        password = 'localadmin'
        print(f'Using default password: {password}')

    # takes one command per execution, the first match
    # --status
    # --force
    # --reboot
    # --[cycle|power_on|power_off]=[all|1-24]
    status = False
    cycle = None
    power_on = None
    power_off = None
    force = False
    reboot = False
    if '--status' in options:
        status = True
    elif '--cycle' in options:
        cycle = options['--cycle']
    elif '--on' in options:
        power_on = options['--on']
    elif '--off' in options:
        power_off = options['--off']
    elif '--force' in options:
        force = True
    elif '--reboot' in options:
        reboot = True
    else:
        exit_with_usage()

    pdu = Tripplite(hostname, username, password)
    print(pdu)
    pdu.connect()

    # status
    if status:
        print(f'Status: {hostname}')
        output_status = pdu.status()
        print(output_status)

    elif reboot:
        print(f'Rebooting ALL loads on {hostname}... ', end='')
        sys.stdout.flush()
        pdu.cycle()
        print('done')

    elif force:
        print(f'Force off ALL loads on {hostname}... ', end='')
        sys.stdout.flush()
        pdu.off()
        pdu.close()
        print('done')

        print('Sleeping for %d minutes... ' % (force_timeout / 60), end='')
        sys.stdout.flush()
        time.sleep(force_timeout)
        print('done')

        pdu.connect()
        print(f'Force on ALL loads on {hostname}... ', end='')
        sys.stdout.flush()
        pdu.on()
        print('done')

    # cycle outlets
    elif cycle is not None:
        if 'all' in cycle:
            # cycle all loads
            print(f'Cycling ALL loads on {hostname}... ', end='')
            sys.stdout.flush()
            pdu.cycle()
            print('done')
        else:
            # cycle specific outlet
            print(f'Cycle load on outlet: {cycle}')

    elif power_on is not None:
        if 'all' in power_on:
            # power on all loads
            print(f'Power on ALL loads on {hostname}... ', end='')
            sys.stdout.flush()
            pdu.on()
            print('done')
        else:
            # power on specific outlet
            print("Power on outlet")

    elif power_off is not None:
        if 'all' in power_off:
            # power off all loads
            print(f'Power off ALL loads on {hostname}... ', end='')
            sys.stdout.flush()
            pdu.off()
            print('done')
        else:
            # power off specific outlet
            print("Power off outlet")


if __name__ == "__main__":
    main()
