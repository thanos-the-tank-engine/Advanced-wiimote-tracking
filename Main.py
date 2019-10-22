"""
Python application for 6DOF tracking of Nintendo Wii controllers and interpretation of resulting data
into various emulated HID devices to enable the use of Wiimotes as a low cost alternative to a commercial 6DOF
controller or tracking system to make this style of input for manipulating objects in CAD, 3D modelling, and gaming
significantly more accessible
"""
import opencv
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
def connectWiimote():
    print "Ready to connect."
    while True:
        try:
            wiimote = cwiid.Wiimote()
        except RuntimeError:
            print 'Failed to connect, try again'
            continue
        break
    wiimote.rpt_mode = cwiid.RPT_IR | cwiid.RPT_BTN | cwiid.RPT_EXT
    print "Connected!"
    print "Battery is at ", (100 * wiimote.state.get('battery') / cwiid.BATTERY_MAX), "%"
    return wiimote


# creates graphical visualization of input data and what the corrector outputs
def graphInputs(pnt_1_x, pnt_2_x, pnt_1_y, pnt_2_y, pnt_1_corr_x, pnt_2_corr_x, pnt_1_corr_y, pnt_2_corr_y):
    plot.cla()
    plot.axis([0, 1024, 0, 768])
    plot.scatter([pnt_1_x, pnt_2_x], [pnt_1_y, pnt_2_y], color='blue', label='raw')
    plot.scatter([pnt_1_corr_x, pnt_2_corr_x], [pnt_1_corr_y, pnt_2_corr_y], color='red', label='corrected')
    plot.legend()
    plot.pause(0.05)
    plot.draw()


# TODO: figure out how the frick I can get libCWiid to give me calibration values for the accelerometer
# TODO: FIX ANGLE CORRECTOR!
"""
TODO: Add an exception to the angle calculator for 90 degrees, incorporate previous values and/or accelerometer data
into angle calculation algorithm to accurately determine the orientation and eliminate the unpredictable values produced
when the controller is at exactly 90 degrees or flipped upside down.    
"""

'''
trigonometry function based calculator for determining the rotation of the controller without needing to use any
sort of computer vision based solution to minimize processing overhead.
only able to provide 3DOF tracking, but has low latency
'''

def handleWiimoteInput(wm):
    state = wm.state
    ir = state['ir_src']
    pnt_1 = ir[0]
    pnt_2 = ir[1]
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
        graphInputs(pnt_1_x, pnt_2_x, pnt_1_y, pnt_2_y, pnt_1_corr_x, pnt_2_corr_x, pnt_1_corr_y, pnt_2_corr_y)
        return output
    else:
        output = dict(x=None, y=None, z=None, btn=state['buttons'])
        return output


# Experimental 6DOF tracking using openCV
# significantly more capable and accurate than trig-based tracker
# but at the cost of latency and performance
# TODO: implement OpenCV 6DOF tracking
def trackWiimote6DOF(wm):
    state = wm.state
    ir = state['ir_src']

