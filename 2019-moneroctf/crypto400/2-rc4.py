import binascii

B = 256
S = []

# Set lists
k = []
c = []
key_hex = '41b60eff56ba1ca585ecb26d4e583cc7e7cd85da6924202b68e6049d5a2fff0a'
ciphertext_hex = '2efe47917b1e7e9f1ea926325ea62c1c90afd46d546bb3f8ba4dcab4e056f6b5d6e8bb4cda2762e0241ab95878bd5e2f897cb9aa4ded6b9a3c7f260cc7cfd42de129680a46efe1555059a360c20daa93b02e32e5442ffc5beb6349ccd673b313f2dba76d6a4e18330a5f43bef15e4e038c9238'
for i in range(len(key_hex)/2):
    k.append(int(key_hex[2*i:2*(i+1)],16))
for i in range(len(ciphertext_hex)/2):
    c.append(int(ciphertext_hex[2*i:2*(i+1)],16))

# Key scheduling
for i in range(B):
    S.append(i)
j = 0
for i in range(B):
    j = (j + S[i] + k[i % len(k)]) % B
    S[i], S[j] = S[j], S[i]

# PRNG
i = 0
j = 0
m = []
for ind in range(len(c)):
    i = (i+1) % B
    j = (j+ S[i]) % B
    S[i], S[j] = S[j], S[i]
    prng_output = S[(S[i] + S[j]) % 256]

    m.append(c[ind] ^ prng_output)

message_hex = ''
for byte in m:
    temp = hex(byte)[2:]
    if len(temp) == 1:
        temp = '0' + temp
    message_hex += temp

print(binascii.unhexlify(message_hex))
