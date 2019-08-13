from dumb25519 import *

a = random_scalar()

def sign(m,x):
    c = hash_to_scalar(m,x*G,a*G)
    s = a - x*c

    return [c,s]

def verify(m,X,c,s):
    c2 = hash_to_scalar(m, X, s*G + c * X)
    return c == c2


X = Point('7a9352fe56753e8eb81f77f82e4ef184d92b9c321d64f5221e48f5f1d9e0afc3')

m1 = 'The lunch order for today? Make it ham on rye, the only sandwich worth eating.'
m2 = 'My order is secret, as always. You know the key.'

c1, s1 = Scalar('cc6d4480a0a7e4efd4ca79f83469b54307ecc41ba087054da89960f67dbf7a08'), Scalar('e7d243d0dac48ac3146fd3b5ea3c290760cc5d4e40f221bb02b8dc9a8bf72700')
c2, s2 = Scalar('387d1a5cc532855f47f35f5519ea16695c8432a8ac553e3b162d1a63b652650e'), Scalar('73f052cf47de792ccb727d3351f18a9bec1ce0f70e70be035709fddf95220d0a')

assert verify(m1, X, c1, s1)
assert verify(m2, X, c2, s2)


k = -((s1 - s2) * (c1 - c2).invert())

print(k)

assert Point(str(G * k)) == X
