from pynput.mouse import Button, Controller

mouse = Controller()

# Read pointer position
print(('The current pointer position is {0}'.format(
    mouse.position)))
print(mouse.position[0])
print(mouse.position[1])

# Set pointer position
mouse.position = (500, 500)
print(('Now we have moved it to {0}'.format(
    mouse.position)))

# Move pointer relative to current position
mouse.move(50, -50)

# Press and release
mouse.press(Button.left)
mouse.release(Button.left)

# Double click; this is different from pressing and releasing
# twice on Mac OSX
mouse.click(Button.left, 2)

# Scroll two steps down
mouse.scroll(0, 2)
