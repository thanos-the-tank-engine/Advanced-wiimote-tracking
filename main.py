import cv2 as opencv
import cwiid
import math
import time
import matplotlib.pyplot as plot
plot.style.use('dark_background')
plot.ion()
"""
  TODO: get semi-accurate numbers for input lag and then determine viability of using an arduino
        to multiplex 4+ IR emitters in different locations around the user to allow true 6DOF tracking
        and work out a potential solution for calibration of such a setup that would work with multiple controllers
"""

# IDE thinks that there is a possibility of the local variable 'wiimote' not getting defined. there is not.
# noinspection PyUnboundLocalVariable
def connect_wiimote():
    print "Ready to connect."
    while True:
        try:
            wiimote = cwiid.Wiimote()
        except RuntimeError:
            print 'Failed to connect, try again'
            continue
        break
    print "Connected!"
    wiimote.enable(cwiid.FLAG_MOTIONPLUS)
    time.sleep(.5)
    # Check if wii remote has a MotionPlus extension and set report mode accordingly
    ext = wiimote.state['ext_type']
    if ext == cwiid.EXT_MOTIONPLUS:
        wiimote.rpt_mode = 143
        print 'MotionPlus detected'
    elif ext == cwiid.EXT_BALANCE:
        wiimote.disable(cwiid.FLAG_MOTIONPLUS)
        wiimote.rpt_mode = 67
        print 'Balance board detected'
    elif ext == cwiid.EXT_NUNCHUK:
        wiimote.disable(cwiid.FLAG_MOTIONPLUS)
        wiimote.rpt_mode = 31
        print 'Nunchuk detected'
    elif ext == cwiid.EXT_CLASSIC:
        wiimote.disable(cwiid.FLAG_MOTIONPLUS)
        wiimote.rpt_mode = 47
        print 'Wii Classic Controller detected'
    elif ext == cwiid.EXT_NONE:
        wiimote.disable(cwiid.FLAG_MOTIONPLUS)
        wiimote.rpt_mode = 15
        print 'No extension detected'
    else:
        wiimote.disable(cwiid.FLAG_MOTIONPLUS)
        wiimote.rpt_mode = 254
        print 'Unknown extension detected'
    print "Battery is at ", (100 * wiimote.state.get('battery') / cwiid.BATTERY_MAX), "%"
    return wiimote


# Handles accelerometer calibration values

def getacc(state, cal):
    lower_cal = cal[0]
    upper_cal = cal[1]
    acc = state['acc']
    return map(handle_cal, acc, lower_cal, upper_cal)


def handle_cal(a, b, c):
    return (a - b) * 255 / (c - b)


# handles MotionPlus data
angle_persistent = [0.0, 0.0, 0.0]
def handle_mp(mesg, b):
    global angle_persistent
    mp = map(handle_mp_cal, mesg[2][1]['angle_rate'])
    angle_persistent = map(add_angle, angle_persistent, mp)
    return dict(abs=angle_persistent, rel=mp, time=b)

def add_angle(a, b):
    c = a + b
    if c < 0:
        c += 360
    if c > 360:
        c -= 360
    return c


def handle_mp_cal(val):
    # convert gyroscope value into degrees/sec by subtracting the offset and dividing by a number from the Wiibrew Wiki
    return float(val - 8192) / 595


# creates graphical visualization of input data and what the corrector outputs
def graph_inputs(pnt_1_x, pnt_2_x, pnt_1_y, pnt_2_y, pnt_1_corr_x, pnt_2_corr_x, pnt_1_corr_y, pnt_2_corr_y):
    plot.cla()
    plot.axis([0, 1024, 0, 768])
    plot.scatter([pnt_1_x, pnt_2_x], [pnt_1_y, pnt_2_y], color='blue', label='raw')
    plot.scatter([pnt_1_corr_x, pnt_2_corr_x], [pnt_1_corr_y, pnt_2_corr_y], color='red', label='corrected')
    plot.legend()
    plot.pause(0.05)
    plot.draw()


'''
trigonometry function based calculator for determining the rotation of the controller without needing to use any
sort of computer vision based solution in order to minimize processing overhead.
only able to track in 3 degrees of freedom, but with lower latency and a faster refresh rate
'''

# TODO: add ability to use gyroscope to continue tracking after controller is no longer pointing at ir emitter
old_pos = [0.0, 0.0, 0.0]
def track_wm_3dof(state, cal):
    global old_pos
    # Get data from controller and break out into separate variables
    ir = state['ir_src']
    pnt_1 = ir[0]
    pnt_2 = ir[1]
    # Convert accelerometer data into more useful form
    acc = getacc(state, cal)
    # Determine if IR data is useful
    if pnt_1.__class__ == dict and pnt_2.__class__ == dict:
        # breaks out IR points into X and Y values
        pnt_1_x = pnt_1['pos'][0]
        pnt_1_y = pnt_1['pos'][1]
        pnt_2_x = pnt_2['pos'][0]
        pnt_2_y = pnt_2['pos'][1]
        #   Names self-explanatory
        delta_x = float(pnt_1_x - pnt_2_x)
        delta_y = float(pnt_1_y - pnt_2_y)
        #   Determine angle of controller based on IR data
        if delta_y == 0:
            angles = [0, 180]
        elif delta_x == 0:
            angles = [90, 270]
        else:
            theta_1 = math.degrees(math.atan(delta_y / delta_x))
            if theta_1 < 0:
                theta_1 += 360
            if theta_1 >= 180:
                theta_2 = theta_1 - 180
            else:
                theta_2 = theta_1 + 180
            angles = [theta_1, theta_2]
        # Choose angle from 2 possibilities based on accelerometer
        if acc[2] < 0:
            angle = angles[0]
        else:
            angle = angles[1]
        # calculate median of IR points to use as output coordinates
        med_x = (pnt_1_x + pnt_2_x) / 2
        med_y = (pnt_1_y + pnt_2_y) / 2
        # combine output data into a dict for ease of use
        old_pos = [med_x, med_y, angle]
        output = dict(x=med_x, y=med_y, z=angle, btn=state['buttons'], ext=None)
    else:
        # if no usable IR data is received, output nothing but button data
        output = dict(x=None, y=None, z=None, btn=state['buttons'], ext=None)
    if state['ext_type'] == 1:
        output['ext'] = state['nunchuk']
    return output

# Experimental 6DOF tracking using openCV
# significantly more capable and accurate than trig-based tracker
# but at the cost of latency, performance, and setup simplicity
# requires a non-standard ir emitter setup, must be rectangular
# TODO: implement OpenCV 6DOF tracking via solvepnp function
# TODO: figure out the hell to use the solvepnp function
def track_wm_6dof(wm):
    image_width = 1024
    image_height = 768
    state = wm.state
    ir = state['ir_src']
    pnt_1 = ir[0]['pos']
    pnt_2 = ir[1]['pos']
    pnt_3 = ir[2]['pos']
    pnt_4 = ir[3]['pos']
    shape = [[-1, -2, 0],
             [1, 2, 0]]
    fx = 1700
    fy = 1700
    cx = image_width / 2
    cy = image_height / 2
    cv = [[fx, 0, cx],
          [0, fy, cy],
          [0, 0, 1]]
    if pnt_1.__class__ == dict and pnt_2.__class__ == dict and pnt_3.__class__ == dict and pnt_4.__class__ == dict:
        points = [pnt_1, pnt_2, pnt_3, pnt_4]
        # No idea if this is right
        opencv.solvePnP(shape, points, cv, 0)
