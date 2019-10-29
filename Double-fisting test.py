import threading
import uinput
import cwiid
import main
wm1 = main.connect_wiimote()
wm2 = main.connect_wiimote()
events = [
    uinput.ABS_X + (0, 255, 0, 0),
    uinput.ABS_Y + (0, 255, 0, 0),
    uinput.ABS_Z + (0, 255, 0, 0),
    uinput.BTN_A,
    uinput.BTN_B,
    uinput.BTN_0,
    uinput.BTN_1,
    uinput.BTN_DPAD_UP,
    uinput.BTN_DPAD_DOWN,
    uinput.BTN_DPAD_LEFT,
    uinput.BTN_DPAD_RIGHT,
    uinput.BTN_2,
    uinput.BTN_3,
    uinput.BTN_4,
    ]
joystick_1 = uinput.Device(events)
joystick_2 = uinput.Device(events)
wm1.led = 1
wm2.led = 2