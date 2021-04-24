from pyzbar import pyzbar
from PIL import Image
info = pyzbar.decode(Image.open('upload/barcode.jpg'))
newstr = info[0][0].decode("utf-8")

print(newstr)