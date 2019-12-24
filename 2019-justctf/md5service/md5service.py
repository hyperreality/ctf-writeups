#!/usr/env python3

# The flag is hidden somewhere on the server, it contains `flag` in its name

import sys
import signal
import subprocess
import os

MODULE = os.path.dirname(__file__)
def user_command():
    return input()

def send(msg):
    print(msg)

def read_file(filename):
    try:
        with open(filename, "r") as f:
            return f.read()
    except:
        return ''


def md5_file(filename):
    out = subprocess.check_output(['/task/md5service.sh'], input=filename.encode(), stderr=subprocess.DEVNULL)
    return out


def main():
    def handler(signum, frame):
        print('Time limit exceeded. Good bye!')
        sys.stdout.flush()
        sys.exit(1)

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(30)

    print("Welcome to md5service!")
    print("I have two commands:")
    print("MD5 <file>     -- will return a md5 for a file")
    print("READ <file>    -- will read a file")

    for i in range(500):
        cmd = input("Cmd: ")
        
        splitted = cmd.split(' ', 1)
        if len(splitted) != 2:
            print('\nBad command. Use MD5|READ <file>')
            continue

        cmd, arg = splitted
        arg = arg.strip()

        if cmd == 'MD5':
            print('Executing MD5 on %r' % arg)
            sys.stdout.flush()
            print('Result:')
            print(md5_file(arg))
        elif cmd == 'READ':
            print('Executing READ on %r' % arg)
            sys.stdout.flush()
            print('RESULT:')
            print(read_file(arg))
        else:
            print('Unrecoginzed command. Try again!')
            sys.stdout.flush()

    print('500 commands limits exceeded. Bye!')
    sys.stdout.flush()

if __name__ == '__main__':
    main()

