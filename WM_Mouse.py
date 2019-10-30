# HID Device emulator- Mouse
import main
from pynput.mouse import Button, Controller
mouse = Controller()
wm = main.connect_wiimote()

while True:
    data = main.track_wm_3dof(wm)
    try:
        x = abs(data['x'] - 1024)
        y = data['y']
        mouse.position = (x*2, y*2)
        wm.led = 1
    except ValueError:
        pass
    except TypeError:
        pass
    if data.__class__ == dict:
        if data['btn'][9]:
            mouse.press(Button.left)
        else:
            mouse.release(Button.left)
        if data['btn'][10]:
            mouse.press(Button.right)
        else:
            mouse.release(Button.right)
