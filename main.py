import cv2 as opencv
import cwiid
import math
import time
from matplotlib import pyplot as plot
plot.ion()

# TODO: comb the spaghetti
"""
  TODO: get semi-accurate numbers for input lag and then determine viability of using an arduino
        to multiplex 4+ IR emitters in different locations around the user to allow true 6DOF tracking
        and work out a potential solution for calibration of such a setup that would work with multiple controllers
"""

# IDE thinks that there is a possibility of the local variable 'wiimote' being unbound.
# this is wrong because when 'wiimote' is not defined it repeats the part that is supposed to define it.
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
    time.sleep(.1)
    wiimote.rpt_mode = cwiid.RPT_IR | cwiid.RPT_BTN | cwiid.RPT_EXT | cwiid.RPT_ACC
    print "Connected!"
    print "Battery is at ", (100 * wiimote.state.get('battery') / cwiid.BATTERY_MAX), "%"
    return wiimote


# Handles accelerometer calibration values

def getacc(wm):
    cal = wm.get_acc_cal(0)
    lower_cal = cal[0]
    upper_cal = cal[1]
    state = wm.state
    acc = state['acc']
    return map(handle_cal, acc, lower_cal, upper_cal)


def handle_cal(a, b, c):
    return (a - b) * 255 / (c - b)


# handles MotionPlus data, converts to usable deg/s values
def handle_motion_plus(state):
    mp = state['motionplus']['angle_rate']
    return map(handle_mp_cal, mp)


def handle_mp_cal(val):
    return float(val - 8192) / float(595)


# creates graphical visualization of input data and what the corrector outputs
def graph_inputs(pnt_1_x, pnt_2_x, pnt_1_y, pnt_2_y, pnt_1_corr_x, pnt_2_corr_x, pnt_1_corr_y, pnt_2_corr_y):
    plot.cla()
    plot.axis([0, 1024, 0, 768])
    plot.scatter([pnt_1_x, pnt_2_x], [pnt_1_y, pnt_2_y], color='blue', label='raw')
    plot.scatter([pnt_1_corr_x, pnt_2_corr_x], [pnt_1_corr_y, pnt_2_corr_y], color='red', label='corrected')
    plot.legend()
    plot.pause(0.05)
    plot.draw()


# TODO: tweak values until this works smoothly
'''
trigonometry function based calculator for determining the rotation of the controller without needing to use any
sort of computer vision based solution in order to minimize processing overhead.
only able to track in 3 degrees of freedom, but with lower latency and a faster refresh rate
'''

# TODO: add ability to use gyroscope to continue tracking after controller is no longer pointing at ir emitter
def track_wm_3dof(wm):
    # Get data from controller and break out into separate variables
    state = wm.state
    ir = state['ir_src']
    pnt_1 = ir[0]
    pnt_2 = ir[1]
    # Convert accelerometer data into more useful form
    acc = getacc(wm)
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
        print angles
        # Choose angle from 2 possibilities based on accelerometer
        if acc[2] < 0:
            angle = math.radians(angles[0])
        else:
            angle = math.radians(angles[1])
        # calculate sine and cosine of angle once for small performance gain
        s = float(math.sin(angle))
        c = float(math.cos(angle))
        # attempt to use a point transformation to correct for rotation of controller
        pnt_1_corr_x = float((pnt_1_x - 512) * c - (pnt_1_y - 384) * s) + 512
        pnt_1_corr_y = float((pnt_1_x - 512) * s - (pnt_1_y - 384) * c) + 384
        pnt_2_corr_x = float((pnt_2_x - 512) * c - (pnt_2_y - 384) * s) + 512
        pnt_2_corr_y = float((pnt_2_x - 512) * s - (pnt_2_y - 384) * c) + 384
        # calculate median of IR points to use as output coordinates
        med_corr_x = ((pnt_1_corr_x + pnt_2_corr_x) - 1024) / -2
        med_corr_y = (pnt_1_corr_y + pnt_2_corr_y) / 2
        # combine output data into a dict for ease of use
        output = dict(x=med_corr_x, y=med_corr_y, z=angle, btn=state['buttons'])
        # graph input data and output data for debugging
        graph_inputs(pnt_1_x, pnt_2_x, pnt_1_y, pnt_2_y, pnt_1_corr_x, pnt_2_corr_x, pnt_1_corr_y, pnt_2_corr_y)
        return output
    else:
        # if no usable IR data is received, output nothing but button data
        output = dict(x=None, y=None, z=None, btn=state['buttons'])
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
