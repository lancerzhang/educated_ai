import numpy as np
import cv2

cap = cv2.VideoCapture('test.mp4')

while cap.isOpened():
    ret, frame = cap.read()
    if frame is None:
        cap = cv2.VideoCapture('test.mp4')
        ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()