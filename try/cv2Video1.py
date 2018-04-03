import numpy as np
import cv2

cap = cv2.VideoCapture('/Users/liuyun/Movies/test.mp4')
i = 1
while (cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (30, 30)
        fontScale = 1
        fontColor = (255, 255, 255)
        lineType = 2
        cv2.putText(frame, str(i),
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)
        cv2.imshow('frame', frame)
        i += 1
        # & 0xFF is required for a 64-bit system
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()
