import cv2
import numpy as np
from PIL import ImageGrab

pil_image = ImageGrab.grab()
full_img = np.array(pil_image)
cv2.imshow('image', full_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
