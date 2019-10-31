import main
import cwiid
import time
import uinput
wiimote = 0
def startup():
    global wiimote
    events = [
        uinput.ABS_X + (-16384, 16384, 128, 0),
        uinput.ABS_Y + (-16384, 16384, 128, 0),
        uinput.BTN_BASE
        ]
    wm_events = [
        uinput.ABS_RX + (0, 1024, 0, 0),
        uinput.ABS_RY + (0, 768, 0, 0),
        uinput.ABS_RZ + (0, 360, 0, 0),
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
        uinput.ABS_HAT0X + (0, 255, 0, 0),
        uinput.ABS_HAT0Y + (0, 255, 0, 0),
        uinput.BTN_5,
        uinput.BTN_6,
    ]
    print 'Connect Balance board first.'
    while True:
        wbc = main.connect_wiimote()
        if wbc.state['ext_type'] != cwiid.EXT_BALANCE:
            print 'ERROR: That isn\'t a balance board. connect the *BALANCE BOARD* first'
            continue
        break
    while True:
        response = raw_input('Connect secondary controller?')
        response.lower()
        if response == 'y' or response == 'yes':
            wiimote = True
            events += wm_events
        elif response == 'n' or response == 'no':
            wiimote = False
        else:
            print 'type yes or no, not ', input
            continue
        break
    if wiimote:
        wm = main.connect_wiimote()
        wm_cal = wm.get_acc_cal(0)
        if wm.state["ext_type"] == cwiid.EXT_NUNCHUK:
            nunchuk = True
            events += nunchuk_events
    else:
        wm = None
        nunchuk = False
    joystick = uinput.Device(events)
    wbc_cal = wbc.get_balance_cal()

    while True:
        # stops it from 100%ing a thread
        time.sleep(0.01)
        state = wbc.state
        data = state['balance']
        bal = [
            32787 * (data['left_bottom'] - wbc_cal[3][0]) / wbc_cal[3][2],
            32787 * (data['right_bottom'] - wbc_cal[1][0]) / wbc_cal[1][2],
            32787 * (data['left_top'] - wbc_cal[2][0]) / wbc_cal[2][2],
            32787 * (data['right_top'] - wbc_cal[0][0]) / wbc_cal[0][2],
        ]
        bal_x = (bal[0] + bal[2])/2 - (bal[1] + bal[3])/2
        bal_y = (bal[0] + bal[1])/2 - (bal[2] + bal[3])/2
        joystick.emit(uinput.ABS_X, int(bal_x), syn=False)
        joystick.emit(uinput.ABS_Y, int(bal_y))
        joystick.emit(uinput.BTN_BASE, state['buttons'] & 8)
        if wiimote:
            wm_state = wm.state
            wm_data = main.track_wm_3dof(wm_state, wm_cal)
            # if good data is provided, split it up into vars x,y, and z.
            if wm_data.__class__ == dict and wm_data['x'] is not None:
                wm_x = wm_data['x']
                wm_y = wm_data['y']
                wm_z = wm_data['z'] * 16
            # If good data is not provided, set vars x,y, and z to 0.
            else:
                wm_x = 0
                wm_y = 0
                wm_z = 0
            # Send x,y, and z values to UInput as joystick axis data
            joystick.emit(uinput.ABS_RX, int(wm_x), syn=False)
            joystick.emit(uinput.ABS_RY, int(wm_y), syn=False)
            joystick.emit(uinput.ABS_RZ, int(wm_z))
            # Pass button presses along to UInput as joystick buttons
            joystick.emit(uinput.BTN_A, wm_data['btn'] & cwiid.BTN_A, syn=False)
            joystick.emit(uinput.BTN_B, wm_data['btn'] & cwiid.BTN_B, syn=False)
            joystick.emit(uinput.BTN_0, wm_data['btn'] & cwiid.BTN_1 > 0, syn=False)
            joystick.emit(uinput.BTN_1, wm_data['btn'] & cwiid.BTN_2, syn=False)
            joystick.emit(uinput.BTN_DPAD_UP, wm_data['btn'] & cwiid.BTN_UP, syn=False)
            joystick.emit(uinput.BTN_DPAD_DOWN, wm_data['btn'] & cwiid.BTN_DOWN, syn=False)
            joystick.emit(uinput.BTN_DPAD_LEFT, wm_data['btn'] & cwiid.BTN_LEFT, syn=False)
            joystick.emit(uinput.BTN_DPAD_RIGHT, wm_data['btn'] & cwiid.BTN_RIGHT, syn=False)
            joystick.emit(uinput.BTN_2, wm_data['btn'] & cwiid.BTN_PLUS, syn=False)
            joystick.emit(uinput.BTN_3, wm_data['btn'] & cwiid.BTN_MINUS, syn=False)
            joystick.emit(uinput.BTN_4, wm_data['btn'] & cwiid.BTN_HOME, syn=True)
            # If nunchuk exists, handle it.
            if nunchuk:
                nunchuk_data = wm_data['ext']
                stick = nunchuk_data['stick']
                nunchuk_btn = nunchuk_data['buttons']
                joystick.emit(uinput.ABS_HAT0X, stick[0], syn=False)
                joystick.emit(uinput.ABS_HAT0Y, stick[1], syn=False)
                joystick.emit(uinput.BTN_5, nunchuk_btn & cwiid.NUNCHUK_BTN_Z, syn=False)
                joystick.emit(uinput.BTN_6, nunchuk_btn & cwiid.NUNCHUK_BTN_C)


startup()
