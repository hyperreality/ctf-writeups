from dumb25519 import *

# I think it's posted to debian?

key = Scalar('8b69a6d6c486d7aa168a91e9839530d95fae72335cc50f50fa165907911c97ee')
m = Scalar(6599370945811077785578244099016099191457712093320052835013283393002424074994)


# "Encrypt"
# c = m + key
# print(c)
# print(c.x)


# "Decrypt"
m = m - key
# print(m)
# print(m.x)

print("https://paste.debian.net/" + str(m.x))

print(hash_to_scalar("Mr. Burns' Casino"))
