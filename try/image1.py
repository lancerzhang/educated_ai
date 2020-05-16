import cv2

img = cv2.imread('image1.jpg', 1)
cv2.imshow('image', img)
k = cv2.waitKey(0) & 0xFF
if k == 27:  # wait for ESC key to exit
    cv2.destroyAllWindows()
elif k == ord('s'):  # wait for 's' key to save and exit
    cv2.imwrite('image1.png', img)
    cv2.destroyAllWindows()
