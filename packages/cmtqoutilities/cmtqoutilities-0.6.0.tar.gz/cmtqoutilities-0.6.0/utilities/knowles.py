from scipy.interpolate import interp1d
import numpy as np


class SR32453000():
    """ Speaker SR-32453-000"""
    def __init__(self):
        freq=[1e2,  2e2,8e2,  1e3,  2e3,2.5e3,3.15e3,4e3,4.2e3,5e3,6e3,8e3,10e3,11e3]
        data=[106.2,107,104.5,105,107,110,116,104,104,98,94.5 , 92, 95,101]
        self.__response=interp1d(freq,data,kind='cubic')
        
        
    
    def __delete__(self):
        pass
        
    def spldB(self,freq):
        """
        Returns returns sound pressure level (SPL) in dB rel 20uPa for 100mV drive.
        
        Parameters
        ==========
        
        freq: array 
            frequencies at which to give the SPL in Hz   
        
        Returns
        =======
        
        array with the SPL
        
        ---
        
        """
        if freq.min()<1e2 or freq.max()>1.1e4:
            raise ValueError('Stay within [100,11000] Hz')
        else:
            return self.__response(freq)
            
    
    def splPa(self,freq):
        """
        Returns returns sound pressure level in Pa rel 20uPa for 100mV drive.
    
        Parameters
        ==========
    
        freq: array 
            frequencies at which to give the SPL in Hz   
    
        Returns
        =======
    
        array with the SPL
    
        ---
    
        """
        if freq.min()<1e2 or freq.max()>1.1e4:
            raise ValueError('Stay within [100,11000] Hz')
        else:
            return 10*20e-6*10**(self.__response(freq)/20)


class FC23629P16():
    """ Microphone FC-23629-P16"""
    
    def __init__(self):
        freq=[1e2,  4e3, 10e3, 20e3]
        data=[-53,-53,-50,-47]
        self.__response=interp1d(freq,data,kind='linear')
        
        
    
    def __delete__(self):
        pass
        
    def sensitivitydB(self,freq):
        """
        Returns returns sensitivity in dB relative to 1V/0.1Pa
        
        Parameters
        ==========
        
        freq: array 
            frequencies at which to give the SPL in Hz   
        
        Returns
        =======
        
        array with the SPL
        
        ---
        
        """
        if freq.min()<1e2 or freq.max()>1.1e4:
            raise ValueError('Stay within [100,11000] Hz')
        else:
            return self.__response(freq)
            
    
    def outputV(self,freq):
        """
        Returns returns output Voltage per Pa
    
        Parameters
        ==========
    
        freq: array 
            frequencies at which to give the SPL in Hz   
    
        Returns
        =======
    
        array with the SPL
    
        ---
    
        """
        if freq.min()<1e2 or freq.max()>1.1e4:
            raise ValueError('Stay within [100,11000] Hz')
        else:
            return 10*10**(self.__response(freq)/20)
            
class normalizer():
    def __init__(self):
        """ Normalize data taken with the FC-23629-P16 -- SR-32453-000 combination """
        
        self.mic=FC23629P16()
        self.speaker=SR32453000()
        
    def normalize(self,f):
        """" Normalize wrt 1kHz """
        ref=1/(self.mic.outputV(np.array([1000]))*self.speaker.splPa(np.array([1000])))
        return 1/(self.mic.outputV(f)*self.speaker.splPa(f))/ref
        
    
    
