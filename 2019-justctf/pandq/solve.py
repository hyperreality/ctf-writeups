#!/usr/bin/env python3

import sys
import signal

from Crypto.Util import number
from Crypto import Random


def pad(msg):
    return msg + chr(29)*29


def unpad(msg):
    n = msg[-1]
    return msg[:-n]


def encrypt(msg, e, n):
    msg = pad(msg)
    m = number.bytes_to_long(msg)
    return hex(pow(m, e, n)).rstrip('L')


def decrypt(cipher, d, n):
    c = int(cipher, 16)
    m = pow(c, d, n)
    msg = number.long_to_bytes(m)
    print(f"before unpad: {msg}")
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
    print(f"after unpad: {msg}")

    if msg == b'justGiveTheFlag!!':
        return "This would give the flag"
    else:
        return "justTryALittleHarder"


p, q = 0, 0
while not (number.isPrime(p) and number.isPrime(q)):
    p = b'justGiveTheFlag!!' + Random.get_random_bytes(14) + b'\x0f'
    p = number.bytes_to_long(p)
    q = (p-1) // 2

print(p.bit_length())
print(q.bit_length())

cipher = hex(p)
print(f"p: {p}")
print(f"q: {q}")
print(f"c: {cipher}")

res = task(p, q, cipher)
print(res)
