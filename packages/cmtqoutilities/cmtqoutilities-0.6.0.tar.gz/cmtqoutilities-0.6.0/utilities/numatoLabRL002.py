import serial
import serial.tools.list_ports

class RL002():
    """
    Class to handle the Numato Lab RL002 Relay.
    
    """
        
    def __init__(self,device=None, name=None, refVoltage = 5):
        """
        Initializes object with default configuration.
        
        Parameters
        ==========
        
        device: string
          Port where the device is attached to. E.g. "/dev/tty.usbmodem41121". Should not
          be used if possible, since ports may change.
        
        name: string
          Serial number of the device to be connected to.
        
        refVoltage: number
          The voltage value with which the device is powered. Is needed for the adc.
        
        Returns
        =======
        
        ---
        
        """
        self.refVoltage = refVoltage
        self.rl002 = None
        self.numatoDevices = self.scanPorts()
        self.device = None
        self.name = None
        foundDevices = True
        if len(self.numatoDevices) == 0:
            print ("No Numato Lab device of type RL002 found.")
            foundDevices = False
        
        if foundDevices:
            dummy = 0
            self.openDevice(device,name)
            
        
    def __delete__(self):
        self.close()
    
    ####################################################################################
    # "Internal methods"
    
    def scanPorts(self):
        """
        Scans the serial ports to find all the Numato Lab devices of type RL002. This 
        is done by searching for the corresponding vendor and product ids.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        List of dictionaries
          Each dictionary represents a valid combination of serial number and device.
        
        """
        ports = list(serial.tools.list_ports.comports())
        numatoDevices =[]
        for p in ports:
            if p.vid == 10777 and p.pid == 3077:
                numatoDevices.append({'device':p.device,'name':self.getNameOf(p.device)})
        return numatoDevices
    
    def openDevice(self,device,name):
        """
        Opens a given Numato Lab RL002 device. The device to be opened can be specified 
        by its port and id name (see parameters below). If the device or 
        name parameter are set to None, it is ignored. In case both parameters are 
        set to None, the first device available is chosen.
        
        Parameters
        ==========
        
        device: string
          Specifier of the device to be openend. Example: '/dev/cu.usbmodem41131'
        
        name: 8-character string
          Id name of the device to be openend.
        
        Returns
        =======
        
        List of dictionaries
          Each dictionary represents a valid combination of port and id name.
        
        """
        tbo = ''
        deviceHappy = device == None
        nameHappy = name == None
        for d in self.numatoDevices:
            if nameHappy and deviceHappy:
                break
            deviceHappy = deviceHappy or device == d['device']
            nameHappy = nameHappy or name == d['name']
        if nameHappy and deviceHappy:
            self.device = d['device']
            self.name = d['name']
            self.rl002 = serial.Serial(self.device, 19200, timeout=1)
        else:
            print("Couldn't find desired RL002 device. Available devices are:")
            print(self.numatoDevices)
    
    def getNameOf(self,device):
        """
        Returns the name of the device connected at a given port device.
        
        Parameters
        ==========
        
        device: string
          Port to which the device is connected.
        
        Returns
        =======
        
        name: string
          Name of the device.
        
        """
        # Open port for communication
        serPort = serial.Serial(device, 19200, timeout=1)
        # Get id
        serPort.write("id get\r")
        serPort.readline()
        devId = serPort.readline().split('\r')[1].split('\n')[0]
        serPort.read(2)
        #Close the port
        serPort.close()
        return devId
    
    ####################################################################################
    # "User" methods
    
    def setName(self,name):
        """
        Sets the name of the device. The name is stored permanently and can be used to
        distinguish different devices of the same type.
        
        Parameters
        ==========
        
        name: 8-character string
          Name to be set. The name needs to be a string of exactly length 8.
        
        Returns
        =======
        
        ---
        
        """
        if len(name) == 8:
            self.rl002.write("id set %s\r"%name)
            self.rl002.readline()
            self.rl002.read(2)
            self.name = name
        else:
            print("Setting device name failed. Make sure the name is exactly 8 characters long.")
    
    def getName(self):
        """
        Returns the name of the device currently connected and openend.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        name: string
          Name of the device.
        
        """
        return self.name
    
    def getVersion(self):
        """
        Returns the version of the device currently connected and openend.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        string
          String containing the current version.
        
        """
        self.rl002.write("ver\r")
        self.rl002.readline()
        version = self.rl002.readline().split('\r')[1].split('\n')[0]
        self.rl002.read(2)
        return version
    
    def setRelay(self,on=True):
        """
        Turns the relay on or off.
        
        Parameters
        ==========
        
        on: bool
          Defines whether the relay should be set to on or off.
        
        Returns
        =======
        
        ---
        
        """
        if on:
            self.rl002.write("relay on 0\r")
        else:
            self.rl002.write("relay off 0\r")
        self.rl002.readline()
        self.rl002.read(2)
    
    def readRelay(self):
        """
        Read the current state of the relay.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        bool
          Bool characterizing the state of the relay. True means relay is on.
        
        """
        self.rl002.write("relay read 0\r")
        self.rl002.readline()
        val = self.rl002.readline().split('\r')[1].split('\n')[0]
        self.rl002.read(2)
        if val in ['on','off']:
            return val == 'on'
        else:
            print("Cannot make sense of the relay state.")
            return None
    
    def setGPIO(self,channel,on=True):
        """
        Sets the gpio channel to high or low.
        
        Parameters
        ==========
        
        channel: int
          Specifies which channel. Available channels are 0,1,2,3.
        
        on: bool
          Specifier whether to set the gpio to 0 (False) or 1 (True).
        
        Returns
        =======
        
        ---
        
        """
        if channel in [0,1,2,3]:
            if on:
                self.rl002.write("gpio set %1i\r"%channel)
                self.rl002.readline()
                self.rl002.read(2)
            else:
                self.rl002.write("gpio clear %1i\r"%channel)
                self.rl002.readline()
                self.rl002.read(2)
        else:
            print("Parameter channel is supposed to be in [0,1,2,3]")
    
    def readGPIO(self,channel):
        """
        Reads the gpio channel for high or low.
        
        Parameters
        ==========
        
        channel: int
          Specifies which channel. Available channels are 0,1,2,3.
        
        Returns
        =======
        
        int
          Integer is either set to 0 or to 1, corresponding to signal low or high at the gpio.
        
        """
        if channel in [0,1,2,3]:
            self.rl002.write("gpio read %i1\r"%channel)
            self.rl002.readline()
            val = self.rl002.readline().split('\r')[1].split('\n')[0]
            self.rl002.read(2)
            return int(val)
        else:
            print("Parameter channel is supposed to be in [0,1,2,3]")
            return None
    
    def readADC(self,channel):
        """
        Reads the analogue voltage at the gpio specified by channel. Note that the response
        depends on self.refVoltage, since the adc's resolution is spread over [0,referenceVoltage]
        where referenceVoltage is the one powering the device.
        
        Parameters
        ==========
        
        channel: int
          Specifies which channel. Available channels are 0,1,2,3.
        
        Returns
        =======
        
        float:
          Measured voltage value.
        
        """
        if channel in [0,1,2,3]:
            self.rl002.write("adc read %i1\r"%channel)
            self.rl002.readline()
            val = self.rl002.readline().split('\r')[1].split('\n')[0]
            self.rl002.read(2)
            return round(self.refVoltage/1023*int(val),3)
        else:
            print("Parameter channel is supposed to be in [0,1,2,3]")
            return None