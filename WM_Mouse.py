# HID Device emulator- Mouse
import main
import cwiid
from pynput.mouse import Button, Controller
mouse = Controller()
wm = main.connect_wiimote()

while True:
    data = main.track_wm_3dof(wm)
    try:
        x = data['x']
        y = data['y']
        mouse.position = (x, y)
        wm.led = 1
    except ValueError:
        wm.led = 15
        main.time.sleep(.1)
        wm.led = 0
        main.time.sleep(.05)
        pass
    if data.__class__ == dict:
        btn = data['btn']
        if btn == cwiid.BTN_A:
            mouse.press(Button.left)
        else:
            mouse.release(Button.left)
        if btn == cwiid.BTN_B:
            mouse.press(Button.right)
        else:
            mouse.release(Button.right)
