from pynput import mouse


def on_click(x, y, button, pressed):
    print 'x:{0} y:{1} button:{2} pressed:{3}'.format(x, y, button, pressed)


with mouse.Listener(on_click=on_click) as listener:
    listener.join()
