# TEMPer-driver-clone
TEMPer driver clone

This driver for my TEMPerV1.4 USB thermometer is adopted from D.P.'s code at neon-society-electronics.com/?p=44.  I put inside a class and modified it somewhat -- it was originally written for version 1.2 of the thermometer and I think that's why it had a runtime error on my raspberry pi. 

Usage:
- mythermometer = TEMPer(0) # where the 0 is for calibration (+/- degreesC)
- tempC = mythermometer.gettemp()
