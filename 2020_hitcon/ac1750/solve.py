from scapy.all import *
from Crypto.Cipher import AES

# https://www.thezdi.com/blog/2020/4/6/exploiting-the-tp-link-archer-c7-at-pwn2own-tokyo
# This article contains a complete explanation of the TP-Link Archer A7 wireless router vulnerability
# The packet capture is of somebody exploiting the vulnerability
# The command execution is typed in one character at a time, which happens to be the 100th byte of each UDP exploit packet after decryption

pkts = rdpcap("ac1750.pcapng")

filtered = [pkt for pkt in pkts if
    UDP in pkt and
    (pkt[IP].dst == "192.168.0.1") and (len(pkt[UDP]) > 200)]

print(len(filtered))

# the first 16 bytes of a static key and IV are used, whoops
KEY = b"TPONEMESH_Kf!xn?gj6pMAt-wBNV_TDP"[:16]
IV = b"1234567890abcdef1234567890abcdef"[:16]
cipher = AES.new(KEY, AES.MODE_CBC, iv=IV)

for p in filtered:
    data = bytes(p[UDP].payload)
    # print(data)
    out = cipher.decrypt(data[16:])
    print(chr(out[100]),end='')

