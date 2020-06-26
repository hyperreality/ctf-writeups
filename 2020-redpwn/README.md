# redpwnCTF 2020

Panda Facts v2
---

In the first version of this challenge, a cookie was created by AES-encrypting the following string:

```javascript
const token = `{"integrity":"${INTEGRITY}","member":0,"username":"${username}"}`
```

The method used to authenticate the token looked questionable, although this time the solution didn't require any crypto. when entering the username, we could just close the double quote and add a second `member` field. Then when the token got decoded and JSON parsed, the value of the second `member` field would override the first, allowing us to become admin and get the flag.


In this second version of the challenge, our first step was to diff the new source code with the old. The token was now an object:

```
const token = {
    integrity: INTEGRITY,
    member: 0,
    username: username
};
```

and it gets JSON-stringified before being encrypted.

Although this is a "web" challenge, we quickly discarded the idea that this was about tricking `JSON.stringify` to insert a second `member` key. Instead, the use of an "integrity" string rather than a HMAC for authentication suggested we could use a CBC bitflip attack.

It's AES-192 CBC mode but the blocks are still 16 bytes long, so encryption of the string "the_cr0wn" would yield ciphertext of the following blocks:

```
{"integrity":"d2		ct[0]
068b64517a277e48		ct[1]
1166b9b488f593",		ct[2]
"member":0,"user		ct[3]
name":"the_cr0wn		ct[4]
"}PPPPPPPPPPPPPP		ct[5]
```

Where `P`  is a PKCS#7 padding byte. We checked the CryptoJS docs and PKCS#7 padding is used for its block ciphers by default.

There are a few ways this attack could be approached, but we thought the simplest was to reuse previous blocks:

```
{"integrity":"d2		ct[0]
068b64517a277e48		ct[1]
1166b9b488f593",		ct[2]
"member":0,"user		ct[3]
name":"the_cr0wn		ct[4]
068b64517a277e48		ct[5]
1166b9b488f593",		ct[6]
```

We could then set `ct[5]  =  ct[5]  XOR  1166b9b488f593",  XOR  aa","member":1}P`. This would give:

```
{"integrity":"d2		ct[0]
068b64517a277e48		ct[1]
1166b9b488f593",		ct[2]
"member":0,"user		ct[3]
name":"the_cr0wn		ct[4]
GARBAGE!GARBAGE!		ct[5]
aa","member":1}P		ct[6]
```

We're causing ct[6] to be decrypted to a block that closes the username string and adds a malicious member field. This is done by XORing the ct[5] block with the XOR between what we actually know is in ct[6] versus what we want. However this would come at the cost of corrupting the decryption of the whole ct[5] block&mdash;because we don't know the key we can't control what it decrypts to after modifying it. We hoped this wouldn't cause a problem in Unicode encoding and decided to just try it.

Initially, we had problems. This was because our corrupted ct[5] blocks ended up containing `"`, `}`, or other bad characters which broke the JSON parsing after server-side decryption. Testing in Python, there were always Unicode errors thrown due to the block of garbage not conforming to UTF-8. For a while, we got stuck. But testing in Node, we found that `JSON.parse` was more tolerant of broken Unicode.

Ultimately we needed to try a few different values in the final block before hitting a decryption of ct[5] which didn't contain a bad char. The whole script is in panda2.py.


Alien Transmissions v2
---

We are given over 1 megabyte of a numeric alien language encrypted by two XOR keys, knowing only that:
 - This alien language consists of words delimitated by the character represented as 481
 - The two keys appear to be of length 21 and 19
 - The value of each character in these keys does not exceed 255

With two XOR keys of coprime lengths, this is similar to using a single key of length 21*19 = 399. The number we are a told is a space is presumably the most common occurrence in the plaintext. Therefore, because our ciphertext is so large, we can easily recover the XOR key: by taking each 399th number, and XOR with 481, we get the key byte in that position. Same with numbers `[1,400,799...]`, and `[2,401,800...]` etc. 

However, the goal of this challenge is to recover both of the keys, whereas now we just have the XOR of each byte of them in all possible 399 positions. At first it seemed impossible to recover a unique solution from this if the keys could contain bytes anywhere in the extended ASCII range, which is what the third point implied.

We loaded up the problem in z3 and started playing with the constraints, narrowing down the solution space to a smaller and smaller alphabet. First we assumed that the output would be all printable bytes. The potential flag output looked better, but we couldn't quite get it. We'd remove letters from the alphabet, looking for a more constrained solution, but z3 was no longer saying it was satisfiable. Eventually we figured out that the flag contained an apostrophe!

The included script solves the challenge using z3, which is overkill but forms a template for more difficult problems.
