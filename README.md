# Advanced-wiimote-tracking
A python application for tracking nintendo wii controllers in 6 degrees of freedom

**This project is still very much a WIP. very little functionality has been implemented in it, and it is nowhere near completion at this time**

This application is designed to allow you to connect wii controllers to a computer and then channel the inputs from it into various emulated HID devices.
The goal of this software is to reduce the barrier of entry for 6DOF controller systems by enabling the use of a relatively low-cost system that can easily be DIY'd out of readily available objects. most current methods, such as the 3d-mouse style of controller, or the controllers used for a VR headset, are incredibly expensive. this software will allow you to accomplish the same thing using something that you probably have lying around already, or can buy secondhand for very little cost if you don't.

Included in this repository:  
\> Python scripts
\> KiCad project containing PCB layout and schematic for an improved sensor bar that expands on the capabilities of the Wii controller by enabling true 6DOF tracking.  
\> 3D model for the optional case of the improved sensor bar

Will be included in the future  
\> Firmware for improved sensor bar  
\> Maybe windows compatibility, if you windows-using plebians get lucky  


#Setup  
Right now, none of the setup process is automated. this means you will have to do it all yourself.
You will need to install my modified version of the Cwiid library that has support for the balance board added to it.
you will have to compile it yourself. I have not bothered trying to run this outside of my IDE because none of the UI exists yet.
If you want to use this on its own, good luck with that. either wait until it's finished or finish it yourself.