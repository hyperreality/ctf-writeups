#!/usr/bin/env python3

import sys
import signal

from Crypto.Util import number
from Crypto import Random

FLAG = open("flag.txt", "r").read()

def pad(msg):
    return msg + chr(29)*29

def unpad(msg):
    n = msg[-1]
    return msg[:-n]

def encrypt(msg, e, n):
    msg = pad(msg)
    m = number.bytes_to_long(msg)
    return hex( pow(m, e, n) ).rstrip('L')

def decrypt(cipher, d, n):
    c = int(cipher, 16)
    m = pow(c, d, n)
    msg = number.long_to_bytes(m)
    return unpad(msg)


# task(int:L, int:L, str:hex)
def task(p, q, cipher):
    n = p*q
    assert p.bit_length() >= 254 and p.bit_length() <= 256, "p is not 254-256 bit long"
    assert q.bit_length() >= 254 and q.bit_length() <= 256, "q is not 254-256 bit long"
    assert number.isPrime(p), "p is not prime"
    assert number.isPrime(q), "q is not prime"

    e = number.getRandomNBitInteger(256)  
    while number.GCD(e, (p-1)*(q-1)) != 1:
        e = number.getRandomNBitInteger(256)

    d = number.inverse(e, (p-1)*(q-1))

    msg = decrypt(cipher, d, n)
    
    if msg == b'justGiveTheFlag!!':
        return FLAG
    else:
        return "justTryALittleHarder"


def main():
    def handler(signum, frame):
        print('Time limit exceeded. Good bye!')
        sys.stdout.flush()
        sys.exit(1)

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(30)

    print("Welcome to p&q Service!")
    print("Give me p,q and cipher encoded as hex and I will tell what the secret was.")
    print("Hopefully...")
    print("Example input")
    print("p: 13337")
    print("q: 7331")
    print("cipher: 0x777777")
    print("Let's start the game!!11!11\n\n")
   
    p = int(input("p: ").strip())
    q = int(input("q: ").strip())
    cipher = input("cipher: ").strip()

    any_luck = task(p,q,cipher)
    
    print("Result:")
    print(any_luck)
    sys.stdout.flush()

if __name__ == '__main__':
    main()
