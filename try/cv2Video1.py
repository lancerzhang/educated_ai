import numpy as np
import cv2
from pynput import keyboard
import threading

cap = cv2.VideoCapture('../train/1440.mp4')


def on_click(x, y, button, pressed):
    print(f'{x}, {y}, {button}, {pressed}')


def on_release(key):
    print(f'{key}')


def run():
    with keyboard.Listener(on_release=on_release) as listener:
        listener.join()


mouse_thread = threading.Thread(target=run)
mouse_thread.daemon = True
mouse_thread.start()

while cap.isOpened():
    ret, frame = cap.read()
    if frame is None:
        cap = cv2.VideoCapture('../train/1440.mp4')
        ret, frame = cap.read()

    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
