import main
import uinput
import time
events = (
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
    )
joystick = uinput.Device(events)
wm = main.connect_wiimote()
time.sleep(1)

while True:
    data = main.track_wm_3dof(wm)
    if data.__class__ == dict and data['x'] != None:
         x = data['x']
         y = data['y']
         z = data['z']
    else:
        x = 0
        y = 0
        z = 0
    btn = data['btn']
    buttons = list(format(btn,'013b'))
    print buttons[0]
    joystick.emit(uinput.ABS_X, int(x), syn=False)
    joystick.emit(uinput.ABS_Y, int(y), syn=False)
    joystick.emit(uinput.ABS_Z, int(z*360)+180)
    joystick.emit(uinput.BTN_A, buttons[9] == '1', syn=False)
    joystick.emit(uinput.BTN_B, buttons[10] == '1', syn=False)
    joystick.emit(uinput.BTN_0, buttons[12] == '1', syn=False)
    joystick.emit(uinput.BTN_1, buttons[11] == '1', syn=False)
    joystick.emit(uinput.BTN_DPAD_UP, buttons[1] == '1', syn=False)
    joystick.emit(uinput.BTN_DPAD_DOWN, buttons[2] == '1', syn=False)
    joystick.emit(uinput.BTN_DPAD_LEFT, buttons[4] == '1', syn=False)
    joystick.emit(uinput.BTN_DPAD_RIGHT, buttons[3] == '1', syn=False)
    joystick.emit(uinput.BTN_2, buttons[0] == '1', syn=False)
    joystick.emit(uinput.BTN_3, buttons[8] == '1', syn=False)
    joystick.emit(uinput.BTN_4, buttons[5] == '1', syn=True)
# For some fucking reason 1 != '1'.
