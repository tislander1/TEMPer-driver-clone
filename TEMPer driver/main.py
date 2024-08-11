import time
import usb

class TEMPer(object):
    #Driver for my TEMPerV1.4 USB thermometer.
    #Adopted from D.P.'s code at neon-society-electronics.com/?p=44.
    #Put inside a class and modified it somewhat -- it was originally
    #written for version 1.2 of the thermometer and thus had a runtime error
    #on my raspberry pi.
    #
    #Usage:
    #mythermometer = TEMPer(0) # where the 0 is for calibration (+/- degreesC)
    #tempC = mythermometer.gettemp()
    
    
    def __init__(self, calibration_C):
        self.VENDOR_ID = 0x0c45
        self.PRODUCT_ID = 0x7401
        self.INTERFACE1 = 0x00
        self.INTERFACE2 = 0x01

        self.reqIntLen=8
        self.reqBulkLen=8
        self.endpoint_Int_in=0x82 #/* endpoint 0x81 address for IN */
        self.endpoint_Int_out=0x00 #/* endpoint 1 address for OUT */

        self.PARAMS1 = [ 0x01, 0x80, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00 ]
        self.PARAMS2 = [ 0x01, 0x82, 0x77, 0x01, 0x00, 0x00, 0x00, 0x00 ]
        self.PARAMS3 = [ 0x01, 0x86, 0xff, 0x01, 0x00, 0x00, 0x00, 0x00 ]

        self.calibration = calibration_C
        self.temper = self.setup_libusb_access()
        
        if (self.temper == None):
            sys.exit(17)

    def setup_libusb_access(self):
        for bus in usb.busses():
            for dev in bus.devices:
                if dev.idVendor == self.VENDOR_ID and dev.idProduct == self.PRODUCT_ID:
                    print "Found the thermometer."
                    return dev
        print "No thermometers found."
        return None

    def ini_control(self,thermometer):
        question = [0x01, 0x01]
        
        # Detaching Kernel drivers on interfaces if any are present
        try:
            thermometer.detachKernelDriver(self.INTERFACE1)
        except:
            pass
        try: 
            thermometer.detachKernelDriver(self.INTERFACE2)
        except:
            pass
        
        # claim interfaces
        try:
            thermometer.claimInterface(self.INTERFACE1)
            thermometer.claimInterface(self.INTERFACE2)
        except:
            print "Couldn't claim one of the interfaces."
        
        r = thermometer.controlMsg(requestType=0x21, request=0x09, value=0x0201, index=self.INTERFACE1, buffer=question)
        if r < 0:
            print "Control Message failed."
            return False
        return True
        
    def control(self, thermometer, question):
        #This function controls the thermometer.  It takes default arguments.
        r = thermometer.controlMsg(requestType=0x21, request=0x09, value=0x0200, index=self.INTERFACE2, buffer=question)
        return
        
    def readin(self, thermometer):
        r = thermometer.interruptRead(self.endpoint_Int_in, self.reqIntLen)
        return
        
    def readin_temperature(self, thermometer):
        answer = thermometer.interruptRead(self.endpoint_Int_in, self.reqIntLen)
        #debug output
        #print "read_temperature answer:"
        #print answer
        tmp = answer[2]
        if (answer[2] & 0x80):
            #The device is working with a signed integer... we don't have that in Python.
            #So whenever the value is greater than 127 we're actually dealing with a negative int
            #print "adjusting negative temp"
            tmp = -0x10 + answer[2]
        
        temperature = (answer[3] & 0xFF) + (tmp << 8)
        temperature += self.calibration
        tempC = temperature * (125.0 / 32000.0)

        return tempC
         
    def usb_release(self, con, iface):
        try:
            con.releaseInterface()
        except:
            pass
        
    def usb_close(self, con):
        con.reset()

    def gettemp(self):
        thermometer = self.temper.open()
        #reset thermometer
        thermometer.reset()

        #Sent control statements to thermometer.
        self.ini_control(thermometer)
        self.control(thermometer, self.PARAMS1 )
        self.readin(thermometer)
        self.control(thermometer, self.PARAMS2 )
        self.readin(thermometer)
        self.control(thermometer, self.PARAMS3 )
        self.readin(thermometer)
        self.readin(thermometer)
        self.control(thermometer, self.PARAMS1)

        #Get the temperature.
        tempc = self.readin_temperature(thermometer)

        #Release the interfaces and close the USB.
        self.usb_release(thermometer, self.INTERFACE1)
        self.usb_release(thermometer, self.INTERFACE2)
        self.usb_close(thermometer)
        return tempc