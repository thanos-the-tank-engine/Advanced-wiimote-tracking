import main
import uinput
events = (
    uinput.BTN_JOYSTICK,
    uinput.ABS_X + (0, 255, 0, 0),
    uinput.ABS_Y + (0, 255, 0, 0),
    uinput.ABS_Z + (0, 255, 0, 0),
    uinput.ABS_RX + (0, 255, 0, 0),
    uinput.ABS_RY + (0, 255, 0, 0),
    uinput.ABS_RZ + (0, 255, 0, 0),
    uinput.ABS_HAT0X + (0, 255, 0, 0),
    uinput.ABS_HAT0Y + (0, 255, 0, 0)
    )
joystick = uinput.Device(events)
wm = main.connect_wiimote()

while True:
    data = main.handle_wm_3dof(wm)
    x = data['x']
    y = data['y']
    z = data['z']
    btn = data['btn']
    buttons = [int(i) for i in list('{0:0b}'.format(btn))]
    print x, ", ", y, ", ", z
    joystick.emit(uinput.ABS_X, int(x))
    joystick.emit(uinput.ABS_Y, int(y))
    joystick.emit(uinput.ABS_Z, int(z*360)+180)
    joystick.emit(uinput.BTN_A, buttons[3])
    joystick.emit(uinput.BTN_B, buttons[2])
    joystick.emit(uinput.BTN_0, buttons[1])
    joystick.emit(uinput.BTN_1, buttons[0])
    joystick.emit(uinput.BTN_DPAD_UP, buttons[11])
    joystick.emit(uinput.BTN_DPAD_DOWN, buttons[10])
    joystick.emit(uinput.BTN_DPAD_LEFT, buttons[8])
    joystick.emit(uinput.BTN_DPAD_RIGHT, buttons[9])
    joystick.emit(uinput.BTN_2, buttons[12])
    joystick.emit(uinput.BTN_3, buttons[4])
    joystick.emit(uinput.BTN_4, buttons[7])
