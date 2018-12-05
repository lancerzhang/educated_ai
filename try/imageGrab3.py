import cv2, time
import numpy as np
from PIL import ImageGrab

start = time.time()
for i in range(0, 10):
    print i
    pil_image = ImageGrab.grab()
print 'used ' + str(time.time() - start)
