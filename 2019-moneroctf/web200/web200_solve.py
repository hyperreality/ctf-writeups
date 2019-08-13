from monero.seed import Seed
import requests
import re
import base64
from PIL import Image
from pyzbar.pyzbar import decode

s = requests.Session()
r = s.get('http://185.10.68.70/poejg4GmvEK4oElmF/web200/lost-and-found-qr.html')

html = r.text
print(html)

reg = re.compile("(iVBO.*)\"")
img = reg.search(html)
imgout = img.group(1)
with open('qr.png', 'wb') as f:
    f.write(base64.b64decode(imgout))

data = decode(Image.open('qr.png'))
print(data)
seed = data[0].data.decode('ascii')
print(seed)

seed = Seed(seed)
addr = seed.public_address()

data = {
    'address': addr
}

r = s.post(
    'http://185.10.68.70/poejg4GmvEK4oElmF/web200/lost-and-found-qr.html', data=data)

print(r.text)
