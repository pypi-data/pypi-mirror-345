import serial
import time
import numpy as np
from utilities import attoIDS3010 as ids
class pressure(object):
    """
    Class to fetch the pressure
    
    """
    def __init__(self, serialPort, baudRate=9600):
        self.serialPort = serialPort;
        self.baudRate = baudRate
        self.serialHandle = serial.Serial(self.serialPort, self.baudRate, bytesize=8, stopbits=1, timeout=1);
        
    def _internal_sendArray(self, transferBuffer):
        self.serialHandle.write(np.array(transferBuffer).astype('ubyte'));
    
    def _internal_sendASCII(self, transferBuffer):
        self.serialHandle.write(transferBuffer)  
    
    def closeConnection(self):
        self.serialHandle.close(); 
        
    def getPressure(self):
        """
        Returns the pressure in mbar
        """
        try:
            self.serialHandle.flush();
            self._internal_sendASCII(b'PR1\r\n');
            self.serialHandle.read_until();
            self._internal_sendArray([5]);
            q = self.serialHandle.read_until();
            result =  float(str(q).split('\\')[0].split(',')[1])
        except:
            result = -1;
        return result;
        
    def flush(self):
        self.serialHandle.flush();
        
    def __delete__(self):
        self.closeConnection()

class temperature(object):
    """
    
    Class to fetch the temperature from the IDS.
    
    """
        
    def __init__(self,address="http://192.168.1.1:8080"):
        self.laser=ids.IDS3010(address)
    
    def getTemperature(self):
        """
        Returns the temperature in centigrade
        """
        return(self.laser.doMethod("com.attocube.ecu.getTemperatureInDegrees")[0])
    