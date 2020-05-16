import pyautogui

# pyautogui.PAUSE = 0.5

pyautogui.size()
# (1366, 768)
width, height = pyautogui.size()

print("screen size", width, height)

for i in range(2):
    pyautogui.moveTo(300, 300, duration=0.25)
    pyautogui.moveTo(400, 300, duration=0.25)
    pyautogui.moveTo(400, 400, duration=0.25)
    pyautogui.moveTo(300, 400, duration=0.25)
