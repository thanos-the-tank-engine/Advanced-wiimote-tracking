# HID Device emulator- Mouse
import Main
import cwiid
from pynput.mouse import Button, Controller
mouse = Controller()
wm = Main.connectWiimote()

#TODO: figure out why this won't work
while True:
    data = Main.handleWiimoteInput(wm)
    if data.__class__ == dict:
        x = data['x']
        y = data['y']
        btn = data['btn']
        mouse.position = (x, y)
        if btn == cwiid.BTN_A:
            mouse.press(Button.left)
        else:
            mouse.release(Button.left)
        if btn == cwiid.BTN_B:
            mouse.press(Button.right)
        else:
            mouse.release(Button.right)
