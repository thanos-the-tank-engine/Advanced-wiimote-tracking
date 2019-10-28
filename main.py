import cv2 as opencv
import cwiid
import math
import matplotlib
matplotlib.use('Qt5Agg')
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
    wiimote.rpt_mode = cwiid.RPT_IR | cwiid.RPT_BTN | cwiid.RPT_EXT | cwiid.RPT_ACC | cwiid.RPT_STATUS
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


# creates graphical visualization of input data and what the corrector outputs
def graph_inputs(pnt_1_x, pnt_2_x, pnt_1_y, pnt_2_y, pnt_1_corr_x, pnt_2_corr_x, pnt_1_corr_y, pnt_2_corr_y):
    plot.cla()
    plot.axis([0, 1024, 0, 768])
    plot.scatter([pnt_1_x, pnt_2_x], [pnt_1_y, pnt_2_y], color='blue', label='raw')
    plot.scatter([pnt_1_corr_x, pnt_2_corr_x], [pnt_1_corr_y, pnt_2_corr_y], color='red', label='corrected')
    plot.legend()
    plot.pause(0.05)
    plot.draw()


"""
TODO: Add an exception to the angle calculator for 90 degrees, incorporate previous values and/or accelerometer data
into angle calculation algorithm to accurately determine the orientation and eliminate the unpredictable values produced
when the controller is at exactly 90 degrees or flipped upside down. 
The formula using ATAN() to get the angle actually has 2 possible outcomes, but only outputs one.
this causes unpredictable values in some cases. this issue can probably be fixed by taking the output and calculating
the other possibility, then selecting one outcome based on some other input, such as the accelerometer.
"""

'''
trigonometry function based calculator for determining the rotation of the controller without needing to use any
sort of computer vision based solution in order to minimize processing overhead.
only able to track in 3 degrees of freedom, but with lower latency and a faster refresh rate
'''
# TODO: add ability to use gyroscope to continue tracking after controller is no longer pointing at ir emitter
def handle_wm_3dof(wm):
    state = wm.state
    ir = state['ir_src']
    pnt_1 = ir[0]
    pnt_2 = ir[1]
    acc = getacc(wm)
    if pnt_1.__class__ == dict and pnt_2.__class__ == dict:
        pnt_1_x = pnt_1['pos'][0]
        pnt_1_y = pnt_1['pos'][1]
        pnt_2_x = pnt_2['pos'][0]
        pnt_2_y = pnt_2['pos'][1]

        delta_x = float(pnt_1_x - pnt_2_x)
        delta_y = float(pnt_1_y - pnt_2_y)
        dist = math.sqrt(math.pow(delta_x, 2) + math.pow(delta_y, 2))

        try:
            angle = float(math.atan(delta_y / delta_x))
        except ZeroDivisionError:
            angle = 0
            pass

        s = float(math.sin(angle))
        c = float(math.cos(angle))

        pnt_1_corr_x = float((pnt_1_x - 512) * c - (pnt_1_y - 384) * s) + 512
        pnt_1_corr_y = float((pnt_1_x - 512) * s - (pnt_1_y - 384) * c) + 384
        pnt_2_corr_x = float((pnt_2_x - 512) * c - (pnt_2_y - 384) * s) + 512
        pnt_2_corr_y = float((pnt_2_x - 512) * s - (pnt_2_y - 384) * c) + 384

        med_corr_x = (pnt_1_corr_x + pnt_2_corr_x) / 2
        med_corr_y = (pnt_1_corr_y + pnt_2_corr_y) / 2
        # combine output data into a dict for easy return
        output = dict(x=med_corr_x, y=med_corr_y, z=angle, btn=state['buttons'])
        graph_inputs(pnt_1_x, pnt_2_x, pnt_1_y, pnt_2_y, pnt_1_corr_x, pnt_2_corr_x, pnt_1_corr_y, pnt_2_corr_y)
        return output
    else:
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
    cv = [[fx,  0, cx],
          [0, fy,  cy],
          [0,   0,  1]]
    if pnt_1.__class__ == dict and pnt_2.__class__ == dict and pnt_3.__class__ == dict and pnt_4.__class__ == dict:
        points = [pnt_1, pnt_2, pnt_3, pnt_4]

