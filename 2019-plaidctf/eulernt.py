#!/usr/bin/env python3

import gmpy2
from decimal import Decimal

N = int(gmpy2.fac(333))
sN = int(gmpy2.isqrt(N))

lastgoodness = 2**32

for i in range(333):
    k = int(gmpy2.fac(i))
    goodness = Decimal(abs(k - sN)) / sN
    print(goodness)
    if goodness > lastgoodness:
        i = i - 1
        break
    lastgoodness = goodness

k = int(gmpy2.fac(i))
factor = i - 1
direction = 0

while not (N % k == 0 and goodness < 1e-8):
    x = int(gmpy2.fac(factor))

    if direction == 0:
        k = k + x
    else:
        k = k - x

    goodness = Decimal(abs(k - sN)) / sN

    print("%s %s %s" % (factor, N % k == 0, goodness))
    if goodness > lastgoodness:
        if factor != 1:
            factor = factor - 1
        direction = direction ^ 1
    lastgoodness = goodness

print("Solution is %s" % k)
