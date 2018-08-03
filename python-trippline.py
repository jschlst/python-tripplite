#!/usr/bin/env python

''' This runs a sequence of commands on a remote PDU using SSH.

./python-tripplite.py -h [ip_address] -u [username] -p [password] --[command]
    -h : hostname of the PDU unit to login to
    -u : username to use for login
    -p : Password to use for login
    --[command] : one of the following
	--status
	--cycle=[all|outlet_num]
	--power_on=[all|outlet_num]
	--power_off=[all|outlet_num]
	--identify

Example:
    This will print information about the given PDU:
        ./python-tripplite.py -h 192.168.2.54 -u localadmin -p localadmin --status
'''

from __future__ import print_function

from __future__ import absolute_import

import os, sys, re, getopt, getpass
import pexpect


try:
    raw_input
except NameError:
    raw_input = input



#
# Some constants.
#
COMMAND_PROMPT = '>> '
# This is the prompt we get if SSH does not have the remote host's public key stored in the cache.
SSH_NEWKEY = '(?i)are you sure you want to continue connecting'

def exit_with_usage():

    print(globals()['__doc__'])
    os._exit(1)

def main():

    global COMMAND_PROMPT, TERMINAL_PROMPT, TERMINAL_TYPE, SSH_NEWKEY
    ######################################################################
    ## Parse the options, arguments, get ready, etc.
    ######################################################################
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h:u:p:', ['status', 'cycle=', 'power_on=', 'power_off=', 'identity'])
    except Exception as e:
        print(str(e))
        exit_with_usage()
    options = dict(optlist)
    if len(args) > 3:
        exit_with_usage()
    print(options)

    if '-h' in options:
        host = options['-h']
    else:
        host = raw_input('hostname: ')
    if '-u' in options:
        user = options['-u']
    else:
        user = raw_input('username: ')
    if '-p' in options:
        password = options['-p']
    else:
        password = getpass.getpass('password: ')


    # XXX: only takes one command per execution, the first match
    # --status
    # --[cycle|power_on|power_off] [all|1-24]
    status    = False
    cycle     = None 
    power_on  = None 
    power_off = None
    identity  = False 
    if '--status' in options:
	status = True
    elif '--cycle' in options:
	cycle = options['--cycle']
    elif '--power_on' in options:
	power_on = options['--power_on']
    elif '--power_off' in options:
	power_off = options['--power_off']
    elif '--identity' in options:
	identity = True


    #
    # Login via SSH
    #
    child = pexpect.spawn('ssh -l %s %s'%(user, host))
    i = child.expect([pexpect.TIMEOUT, SSH_NEWKEY, COMMAND_PROMPT, '(?i)password'])
    if i == 0: # Timeout
        print('ERROR! could not login with SSH. Here is what SSH said:')
        print(child.before, child.after)
        print(str(child))
        sys.exit (1)
    if i == 1: # In this case SSH does not have the public key cached.
        child.sendline ('yes')
        child.expect ('(?i)password')
    if i == 2:
        # This may happen if a public key was setup to automatically login.
        # But beware, the COMMAND_PROMPT at this point is very trivial and
        # could be fooled by some output in the MOTD or login message.
        pass
    if i == 3:
        child.sendline(password)
	child.expect(COMMAND_PROMPT)
	#print(child.before)


    # Now we should be at the command prompt and ready to run some commands.

    # Devices Menu
    child.sendline ('1')
    child.expect (COMMAND_PROMPT)
    #print(child.before)


    # Status Menu
    if status:
	print('status')
	child.sendline ('1')
	child.expect (COMMAND_PROMPT)
	print(child.before)
    elif cycle != None:
	print('cycle: %s'%(cycle))
        child.sendline ('3')
        child.expect (COMMAND_PROMPT)
        print(child.before)

	# cycle all loads
        child.sendline ('6')
        child.expect (COMMAND_PROMPT)
        print(child.before)

	child.sendline ('Y')
        child.expect (COMMAND_PROMPT)
        print(child.before)

    elif power_on != None:
	print('power_on: %s'%(power_on))
        child.sendline ('3')
        child.expect (COMMAND_PROMPT)
        print(child.before)

        # Turn all loads on
        child.sendline ('9')
        child.expect (COMMAND_PROMPT)
        print(child.before)

        child.sendline ('Y')
        child.expect (COMMAND_PROMPT)
        print(child.before)


    elif power_off != None:
	print('power_off: %s'%(power_off))
        child.sendline ('3')
        child.expect (COMMAND_PROMPT)
        print(child.before)

        # Turn all loads off
        child.sendline ('5')
        child.expect (COMMAND_PROMPT)
        print(child.before)

        child.sendline ('Y')
        child.expect (COMMAND_PROMPT)
        print(child.before)
    elif identity != None:
	print('identity: %s'%(identity))
        child.sendline ('2')
        child.expect (COMMAND_PROMPT)
        print(child.before)


    # Now exit the remote host.
    child.sendline ('M')
    child.expect (COMMAND_PROMPT)
    #print(child.before)

    child.sendline ('Q')
    #print(child.before)
    child.expect(pexpect.EOF)

if __name__ == "__main__":
    main()
