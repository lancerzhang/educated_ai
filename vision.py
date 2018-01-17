from PIL import ImageGrab
from PIL import Image
from win32api import GetSystemMetrics

# 1920	960	320	80	16
# 1080	540	180	45	9

screen_width = GetSystemMetrics(0)
screen_height = GetSystemMetrics(1)

grab_width = 32
grab_height = 32


# grab a fix size region with specified zoom level from screen
# x1,y1 is starting position (left top)
def grab(level=1, x1=screen_width / 2, y1=screen_height / 2):
    if x1 >= screen_width or y1 >= screen_height:
        return None
    x2 = x1 + grab_width * level
    y2 = y1 + grab_height * level
    new_width = grab_width
    new_height = grab_height
    if x2 > screen_width:
        new_width = (screen_width - x1) / level
        x2 = screen_width
    if y2 > screen_height:
        new_height = (screen_height - y1) / grab_width
        y2 = screen_height
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    if level > 1:
        img = img.resize((new_width, new_height), Image.ANTIALIAS)
    return img
