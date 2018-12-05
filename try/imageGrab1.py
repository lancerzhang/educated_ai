from PIL import ImageGrab
from PIL import Image

img = ImageGrab.grab()  
img.save('screen1.jpg','JPEG')

img = img.resize((960,540), Image.ANTIALIAS)
img.save('screen1-2.jpg')

img = img.resize((320,180), Image.ANTIALIAS)
img.save('screen1-3.jpg')

img = img.resize((80,45), Image.ANTIALIAS)
img.save('screen1-4.jpg')

img = img.resize((16,9), Image.ANTIALIAS)
img.save('screen1-5.jpg')

img2=ImageGrab.grab(bbox=(100,100,1000,1000))
img2.save('screen2.jpg','JPEG')