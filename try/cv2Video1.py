import numpy as np
import cv2

cap = cv2.VideoCapture('/Users/liuyun/Movies/test.mp4')
# get frame info
width = str(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = str(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fil1 = np.array([[-1, -1, 0],
                [-1, 0, 1],
                [0, 1, 1]])
fil2 = np.array([[1, 0, -1],
                 [0, 0, 0],
                 [-1, 0, 1]])

i = 1
while (cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        # crop
        y=0; x=0; w=500; h=500
        roi = frame[y:y + h, x:x + w]
        # filter
        img = cv2.filter2D(roi, -1, fil2)
        # add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (30, 30)
        fontScale = 1
        fontColor = (255, 255, 255)
        lineType = 2
        text=str(i)+", w "+width+", h "+height
        cv2.putText(img, text,
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)
        cv2.imshow('frame', img)
        i += 1
        # & 0xFF is required for a 64-bit system
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()
