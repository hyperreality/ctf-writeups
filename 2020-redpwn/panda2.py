import base64
import itertools
import json
import requests
import string


def xor(a, b):
    return bytes([c ^ d for c, d in zip(a, b)])


# b'{"integrity":"d2068b64517a277e481166b9b488f593","member":0,"username":"the_cr0wn"}PPPPPPPPPPPPPP'
token = "fZqSs1QL9eFzxnQqk/fM31dqhJTTrkecr8bOx9A3hIoKPfCgKrnibfegbWlicHyM288mgNmhHH2ZPa86iKESNLnLayDPBEv6xsQarxM2hcOYAGabcwlNnD/rvCG/Rc8J"
b64d = base64.b64decode(token)
assert len(b64d) == 96

blocks = [b64d[i:i+16] for i in range(0, len(b64d), 16)]
print(blocks)

middle = b'068b64517a277e48'
middle_block = blocks[1]  # enc(068b64517a277e48)
end = b'1166b9b488f593",'
end_block = blocks[2]  # enc(1166b9b488f593")


for comb in itertools.permutations(string.ascii_lowercase, 2):
    comb = ''.join(comb)
    wanted = comb.encode() + b'","member":1}\x01'
    assert len(wanted) == 16

    new_middle = xor(xor(wanted, end), middle_block)

    new_blocks = blocks[:5]
    new_blocks.append(new_middle)
    new_blocks.append(end_block)

    joined = b''.join(new_blocks)
    b64d = base64.b64encode(joined)
    print(b64d.decode())

    cookies = {
        'token': b64d.decode()
    }
    response = requests.get(
        'https://panda-facts-v2.2020.redpwnc.tf/api/flag', cookies=cookies)

    print(response.text)
    if 'flag' in response.text:
        break
