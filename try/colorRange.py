from components.filter_colors import FilterColors
import cv2

img = cv2.imread('triangle1.jpg', 1)
# im = cv2.imread('../debug/img/00cc9631e55563f592b77ffba57346e946bf22a2.jpg', 1)
fc = FilterColors(img)
cv2.imshow("Result", fc.get_filtered_color_image(2))

# hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# mask = cv2.inRange(hsv, (114,10,1), (132,255,255))
# res = cv2.bitwise_and(img,img, mask= mask)
# cv2.imshow("Result", res)
cv2.waitKey(0)
cv2.destroyAllWindows()
