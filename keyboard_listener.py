from pynput import keyboard
import constants
import logging

logger = logging.getLogger('InputListener')
logger.setLevel(logging.INFO)


class KeyboardListener(object):
    key = ''

    def __init__(self):
        return

    def start(self):
        with keyboard.Listener(on_release=self.on_release) as listener:
            listener.join()

    def get_key(self):
        pressed_key = self.key
        self.key = ''
        return pressed_key

    def on_release(self, key):
        # Mac only can monitor some special key, others need to run as admin
        if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.key = constants.KEY_CTRL
        elif key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            self.key = constants.KEY_ALT
        elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
            self.key = constants.KEY_SHIFT
