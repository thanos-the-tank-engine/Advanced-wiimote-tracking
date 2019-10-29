import threading
import uinput
import cwiid
import main
wm1 = main.connect_wiimote()
wm2 = main.connect_wiimote()
events = (
    uinput.BTN_0,
    uinput.BTN_1,
    uinput.BTN_2,
    uinput.BTN_3,
    uinput.ABS_X + (0, 255, 0, 0),
    uinput.ABS_Y + (0, 255, 0, 0),
    uinput.ABS_Z + (0, 255, 0, 0),
    uinput.ABS_RX + (0, 255, 0, 0),
    uinput.ABS_RY + (0, 255, 0, 0),
    uinput.ABS_RZ + (0, 255, 0, 0)
    )

joystick = uinput.Device(events)
wm1.led = 1
wm2.led = 2

# TODO: complete input handling, separate handling for each controller onto it's own thread
while True:
    data1 = main.track_wm_3dof(wm1)
    data2 = main.track_wm_3dof(wm2)
