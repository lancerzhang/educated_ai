from pynput import keyboard
from . import constants
from . import util
import logging

logger = logging.getLogger('InputListener')
logger.setLevel(logging.INFO)


class KeyboardListener(object):
    running = True
    key = ''

    @util.timeit
    def __init__(self):
        return

    @util.timeit
    def run(self):
        logging.info('start KeyboardListener thread')
        with keyboard.Listener(on_release=self.on_release) as listener:
            listener.join()

    @util.timeit
    def get_key(self):
        pressed_key = self.key
        self.key = ''
        return pressed_key

    @util.timeit
    def on_release(self, key):
        # Mac only can monitor some special key, others need to run as admin
        if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.key = constants.KEY_CTRL
        elif key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            self.key = constants.KEY_ALT
        elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
            self.key = constants.KEY_SHIFT
