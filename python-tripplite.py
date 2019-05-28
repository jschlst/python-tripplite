#!/usr/bin/env python

''' This runs a sequence of commands on a remote Tripp Lite PDU.

Written by Jay Schulist <jayschulist@gmail.com>
Version 0.1.0
Date 05/27/2019

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
'''

from __future__ import print_function

from __future__ import absolute_import

import os, sys, re, getopt, getpass
import pexpect
import time

try:
    raw_input
except NameError:
    raw_input = input



#
# Some constants.
#
COMMAND_PROMPT = '>> '

# This is the prompt we get if SSH does not have the remote host's public key stored in the cache.
#SSH_NEWKEY = '(?i)are you sure you want to continue connecting'

def exit_with_usage():
    print(globals()['__doc__'])
    os._exit(1)

def send_command(child, menu_num=None, prompt=COMMAND_PROMPT, quiet=False):
        print(str(child))

def main():

    global COMMAND_PROMPT, TERMINAL_PROMPT, TERMINAL_TYPE, SSH_NEWKEY
    ######################################################################
    ## Parse the options, arguments, get ready, etc.
    ######################################################################
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h:u:p:', ['status', 'cycle=', 'on=', 'off='])
    except Exception as e:
        print(str(e))
        exit_with_usage()
    options = dict(optlist)
    if len(args) > 3:
        exit_with_usage()
    #print(options)

    if '-h' in options:
        hostname = options['-h']
    else:
        hostname = raw_input('hostname: ')
    if '-u' in options:
        username = options['-u']
    else:
        username = raw_input('username: ')
    if '-p' in options:
        password = options['-p']
    else:
        password = getpass.getpass('password: ')


    # takes one command per execution, the first match
    # --status
    # --[cycle|power_on|power_off] [all|1-24]
    status    = False
    cycle     = None 
    power_on  = None 
    power_off = None
    if '--status' in options:
	status = True
    elif '--cycle' in options:
	cycle = options['--cycle']
    elif '--on' in options:
	power_on = options['--on']
    elif '--off' in options:
	power_off = options['--off']
    else:
        exit_with_usage()


    #
    # Login via telnet (SSH doesn't work with pexpect) 
    #
    child = pexpect.spawn('telnet %s' % hostname)
    child.logfile = open('tripplite.log', 'w')
    child.expect('Username: ')
    child.sendline('%s' % username)
    child.expect('Password: ')
    child.sendline('%s' % password)
    print('telnet connected to %s@%s' % (username, hostname))

    '''
    # SSH login works, but menu commands do not
    child = pexpect.spawn('ssh -l %s %s'%(username, hostname))
    child.logfile = open('tripplite.log', 'w')
    child.delaybeforesend = 3 
    child.delayaftersend = 3
    #child.logfile = sys.stdout
    #child.setecho(False)
    #child.delaybeforesend = None
    i = child.expect([pexpect.TIMEOUT, SSH_NEWKEY, COMMAND_PROMPT, '(?i)password:'])
    if i == 0: # Timeout
        print('ERROR! could not login with SSH. Here is what SSH said:')
        print(child.before, child.after)
        print(str(child))
        sys.exit (1)
    if i == 1: # In this case SSH does not have the public key cached.
	print('no ssh key cached')
        child.sendline ('yes')
        child.expect ('(?i)password:')
    if i == 2:
        print('option 2')
        # This may happen if a public key was setup to automatically login.
        # But beware, the COMMAND_PROMPT at this point is very trivial and
        # could be fooled by some output in the MOTD or login message.
        pass
    if i == 3:
        child.sendline(password)
        print('ssh connected.')
    '''

    # Now we should be at the command prompt and ready to run some commands.

    # Devices Menu
    child.expect(COMMAND_PROMPT)
    child.sendline('1')

    # status
    if status:
        print('Status: %s' % hostname)
        child.expect(COMMAND_PROMPT)
        child.sendline('1')
        child.expect(COMMAND_PROMPT)
        output_status = child.before[92:-75]
        print(output_status)

    # cycle outlets
    elif cycle != None:
	if 'all' in cycle:
	    # cycle all loads
            print('Cycling ALL loads on %s... ' % hostname, end='')
            sys.stdout.flush()
            child.expect(COMMAND_PROMPT)
            child.sendline('3')
            child.expect(COMMAND_PROMPT)
            child.sendline('6')
            child.expect(COMMAND_PROMPT)
            child.sendline('Y')
            print('done')
	else:
	    # cycle specific outlet
            print('Cycle load on outlet: %s' % cycle)
	    send_command(child, '5')
	    send_command(child, '1')
	    send_command(child, cycle)
	    send_command(child, '4')
	    send_command(child, 'Y')

    elif power_on != None:
	if 'all' in power_on:
	    # power on all loads
            print('Power on ALL loads on %s... ' % hostname, end='')
            sys.stdout.flush()
            child.expect(COMMAND_PROMPT)
            child.sendline('3')
            child.expect(COMMAND_PROMPT)
            child.sendline('9')
            child.expect(COMMAND_PROMPT)
            child.sendline('Y')
            print('done')
	else:
	    # power on specific outlet
            send_command(child, '5')
            send_command(child, '1')
            send_command(child, power_on)
            send_command(child, '3')
	    send_command(child, 'Y')

    elif power_off != None:
	if 'all' in power_off:
	    # power off all loads
            print('Power off ALL loads on %s... ' % hostname, end='')
            sys.stdout.flush()
            child.expect(COMMAND_PROMPT)
            child.sendline('3')
            child.expect(COMMAND_PROMPT)
            child.sendline('5')
            child.expect(COMMAND_PROMPT)
            child.sendline('Y')
            print('done')
	else:
	    # power off specific outlet
	    send_command(child, '5')
            send_command(child, '1')
            send_command(child, power_off)
            send_command(child, '3')
	    send_command(child, 'Y')

    # Now exit the remote host and close the connection.
    child.sendline('M')
    child.expect(COMMAND_PROMPT)
    child.sendline ('Q')
    child.close()

if __name__ == "__main__":
    main()
