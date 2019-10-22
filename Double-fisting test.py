import uinput
import cwiid
import Main
wm1 = Main.connectWiimote()
wm2 = Main.connectWiimote()
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
        uinput.ABS_RZ + (0, 255, 0, 0),
        uinput.ABS_HAT0X + (0, 255, 0, 0),
        uinput.ABS_HAT0Y + (0, 255, 0, 0),
        uinput.ABS_HAT1X + (0, 255, 0, 0),
        uinput.ABS_HAT1Y + (0, 255, 0, 0),
        )

joystick = uinput.Device(events)
wm1.led = 1
wm2.led = 2

while True:
    state1 = wm1.state
    state2 = wm2.state
    acc1 = state1.get('acc')
    acc2 = state2.get('acc')
    ir1 = state1['ir_src']
    ir2 = state2['ir_src']
    print ir1, ir2