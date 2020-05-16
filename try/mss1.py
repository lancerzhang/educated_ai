import cv2
import mss
import numpy

# with mss() as sct:
#     sct.shot()
mon = {"top": 40, "left": 1000, "width": 800, "height": 640}
title = "[MSS] FPS benchmark"
sct = mss.mss()
img = numpy.asarray(sct.grab(mon))
cv2.imshow(title, img)
cv2.waitKey(0)
cv2.destroyAllWindows()
