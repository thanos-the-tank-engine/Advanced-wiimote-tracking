import main
import uinput
import time
import cwiid
nunchuk = 0
cal = None
def start():
    events = [
        uinput.ABS_X + (0, 1024, 0, 0),
        uinput.ABS_Y + (0, 768, 0, 0),
        uinput.ABS_Z + (0, 360, 0, 0),
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
    nunchuk_events = [
        uinput.ABS_RX + (0, 255, 0, 0),
        uinput.ABS_RY + (0, 255, 0, 0),
        uinput.BTN_5,
        uinput.BTN_6,
    ]
    global nunchuk
    wm = main.connect_wiimote()
    wm.led = 1
    # If Nunchuk is connected, add extra events to support it
    if wm.state['ext_type'] == 1:
        events += nunchuk_events
        nunchuk = 1
    joystick = uinput.Device(events)
    global cal
    cal = wm.get_acc_cal(0)
    while True:
        time.sleep(.05)
        wm_joystick(wm, joystick)


def wm_joystick(wm, joystick):
    global cal
    global nunchuk
    data = main.track_wm_3dof(wm.state, cal)
    # if good data is provided, split it up into vars x,y, and z.
    if data.__class__ == dict and data['x'] is not None:
        x = data['x']
        y = data['y']
        z = data['z'] * 16
    # If good data is not provided, set vars x,y, and z to 0.
    else:
        x = 0
        y = 0
        z = 0
    # Send x,y, and z values to UInput as joystick axis data
    joystick.emit(uinput.ABS_X, int(x), syn=False)
    joystick.emit(uinput.ABS_Y, int(y), syn=False)
    joystick.emit(uinput.ABS_Z, int(z))
    # Pass button presses along to UInput as joystick buttons
    joystick.emit(uinput.BTN_A, data['btn'] & cwiid.BTN_A, syn=False)
    joystick.emit(uinput.BTN_B, data['btn'] & cwiid.BTN_B, syn=False)
    joystick.emit(uinput.BTN_0, data['btn'] & cwiid.BTN_1 > 0, syn=False)
    joystick.emit(uinput.BTN_1, data['btn'] & cwiid.BTN_2, syn=False)
    joystick.emit(uinput.BTN_DPAD_UP, data['btn'] & cwiid.BTN_UP, syn=False)
    joystick.emit(uinput.BTN_DPAD_DOWN, data['btn'] & cwiid.BTN_DOWN, syn=False)
    joystick.emit(uinput.BTN_DPAD_LEFT, data['btn'] & cwiid.BTN_LEFT, syn=False)
    joystick.emit(uinput.BTN_DPAD_RIGHT, data['btn'] & cwiid.BTN_RIGHT, syn=False)
    joystick.emit(uinput.BTN_2, data['btn'] & cwiid.BTN_PLUS, syn=False)
    joystick.emit(uinput.BTN_3, data['btn'] & cwiid.BTN_MINUS, syn=False)
    joystick.emit(uinput.BTN_4, data['btn'] & cwiid.BTN_HOME, syn=True)
    # If nunchuk exists, handle it.
    if nunchuk:
        nunchuk_data = data['ext']
        stick = nunchuk_data['stick']
        nunchuk_btn = nunchuk_data['buttons']
        joystick.emit(uinput.ABS_RX, stick[0], syn=False)
        joystick.emit(uinput.ABS_RY, stick[1], syn=False)
        joystick.emit(uinput.BTN_5, nunchuk_btn & cwiid.NUNCHUK_BTN_Z, syn=False)
        joystick.emit(uinput.BTN_6, nunchuk_btn & cwiid.NUNCHUK_BTN_C)

start()