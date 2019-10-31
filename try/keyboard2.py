from components.keyboard_listener import KeyboardListener
from components.mouse_listener import MouseListener
import schedule
import threading
import time


def schedule_action1():
    print('schedule action1')


def schedule_action2():
    print('schedule action2')


def run_pending():
    while 1:
        schedule.run_pending()
        time.sleep(1)


schedule.every(5).seconds.do(schedule_action1)
schedule.every(59).seconds.do(schedule_action2)
schedule_thread = threading.Thread(target=run_pending)
schedule_thread.daemon = True
schedule_thread.start()

mouse_listener = MouseListener()
mouse_thread = threading.Thread(target=mouse_listener.run)
mouse_thread.daemon = True
mouse_thread.start()

keyboard_listener = KeyboardListener()
keyboard_thread = threading.Thread(target=keyboard_listener.run)
keyboard_thread.daemon = True
keyboard_thread.start()

while 1:
    time.sleep(0.1)
    button = mouse_listener.get_button()
    if button and len(button) > 0:
        print(f'button is {button}')
    key = keyboard_listener.get_key()
    if key and len(key) > 0:
        print(f'key is {key}')
    if key is 'shift':
        break
