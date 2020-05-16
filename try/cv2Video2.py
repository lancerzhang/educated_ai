import cv2

from components import util

cap = cv2.VideoCapture('D:/bak/test.mkv')
frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

img = cv2.imread('head11.jpg', 1)
reg_point = cv2.resize(img, (1, 1))
reg_cat = util.sort_color(reg_point[0, 0])
hash_size = 3
reg_hash = util.image_hash(img, hash_size)
hist_size = 3
reg_img = cv2.resize(img, (hist_size, hist_size))
steps = 64
windows = [64, 128, 192, 256]

while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        for s in range(0, 4):
            positionX = steps * s
            positionY = steps * s
            for w in range(0, len(windows)):
                width_windows = int(frame_width / windows[w])
                for i in range(0, width_windows):
                    height_windows = int(frame_height / windows[w])
                    for j in range(0, height_windows):
                        newX = windows[w] * i
                        newY = windows[w] * j
                        endX = newY + windows[w]
                        endY = newY + windows[w]
                        if endX <= frame_width and endY <= frame_height:
                            roi_img = frame[newY:newY + windows[w], newX:newX + windows[w]]
                            roi_point = cv2.resize(roi_img, (1, 1))
                            roi_cat = util.sort_color(roi_point[0, 0])
                            roi_hash = util.image_hash(roi_img, hash_size)
                            hash_dist = util.hamming(roi_hash, reg_hash)
                            # hist_sim=util.color_hist_similarity(reg_img, roi_img, hist_size)
                            # if roi_cat == reg_cat and hash_dist < 3 and hist_sim > 0.6:
                            if roi_cat == reg_cat and hash_dist < 3:
                                cv2.rectangle(frame, (newX, newY), (newX + windows[w], newY + windows[w]), (0, 255, 0),
                                              1)
            cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
