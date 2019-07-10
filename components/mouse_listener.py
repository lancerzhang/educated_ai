from pynput import mouse
from . import constants
from . import util
import logging

logger = logging.getLogger('MouseListener')
logger.setLevel(logging.INFO)


class MouseListener(object):
    running = True
    button = ''

    @util.timeit
    def __init__(self):
        return

    @util.timeit
    def run(self):
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

    @util.timeit
    def get_button(self):
        pressed_button = self.button
        self.button = ''
        return pressed_button

    @util.timeit
    def on_click(self, x, y, button, pressed):
        if button is mouse.Button.left and pressed:
            self.button = constants.LEFT_CLICK
