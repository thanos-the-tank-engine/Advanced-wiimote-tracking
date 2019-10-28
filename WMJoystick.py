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

# TODO: add button handling
while True:
    data = main.handle_wm_3dof(wm)
    x = data['x']
    y = data['y']
    z = data['z']
    btn = data['btn']
    print x, ", ", y, ", ", z
    joystick.emit(uinput.ABS_X, int(x))
    joystick.emit(uinput.ABS_Y, int(y))
    joystick.emit(uinput.ABS_Z, int(z*360)+180)
