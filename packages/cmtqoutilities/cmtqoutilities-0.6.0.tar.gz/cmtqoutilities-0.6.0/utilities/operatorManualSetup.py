from __future__ import division
import utilities.operator as operator
import utilities.ps4000a as ps4000a
import utilities.attoIDS3010 as IDS3010
import utilities.zaberLRQ600 as LRQ600
import utilities.lockIn as lockIn
import utilities.lcAO4 as lcAO4
import utilities.numatoLabRL002 as numatoLabRL002

class OperatorManualSetup(operator.Operator):
    """
    Operator class for manual setups.
    
    This class inherits from the Operator class which contains the general structure how we want to operate our experiments -- so, check out its help as well!
    
    """
    # Name of this setup
    @property
    def setupName(self):
        return "manualSetup"
    
    # Include marker which specifies which text parts are taken from a Jupyter notebook when starting an experiment.
    @property
    def includeMarker(self):
        return super(OperatorManualSetup,self).includeMarker
    
    # Exclude marker which specifies which text parts are left out from a Jupyter notebook when starting an experiment.
    @property
    def excludeMarker(self):
        return super(OperatorManualSetup,self).excludeMarker
    
    # Relative path to user defined libraries. Files in these paths are copied to the data directory to ensure reproducability.
    @property
    def userDefinedLibraryDirs(self):
        # paths speficied by the mother class
        libs = super(OperatorManualSetup,self).userDefinedLibraryDirs
        # additional paths
        # libs.append("vibrometer/utilities")
        return libs
    
    # Lines which start with the below wording will be commented out when creating the python file run.py
    @property
    def lineIgnoreKeys(self):
        liks = super(OperatorManualSetup,self).lineIgnoreKeys
        return liks
    
    def __init__(self,devices = None,printExceptions = True):
        """
        Create an OperatorManualSetup instance.
        
        Parameters
        ==========
        
        devices: dict
          Dictionary in the form of key, list pairs. Key identfies the different types of devices. The list contains identifiers of individual devices of type key.
        
        printExceptions: bool
          Boolean specifying whether or not to print exception messages.
        
        Returns
        =======
        
        ---
        
        """
        super(OperatorManualSetup,self).__init__()
        self.printExceptions = printExceptions
        self.dev={}
        if devices == None:
            devices = {}
            print("No devices chosen. Devices used in the past are")
            print("  IDS3010 / http://192.168.1.1:8080")
            print("  ps4000a / DU015/026")
            print("  ps4000a / DX129/188")
            print("  LRQ600  / /dev/tty.usbserial-A104BY60")
            print("  lockIn  / marc")
            print("  lcAO4  / 1326055424")
            print("  numatoLabRL002  / espress0")
        for key in devices.keys():
            for devType in devices[key].keys():
                try:
                    if devType == 'IDS3010':
                        # create attocube instance
                        self.dev[key] = IDS3010.IDS3010(devices[key][devType])
                        # get the resolution which is configured in the laser
                        try:
                            self.dev[key].getResolution()
                        except Exception, e: 
                            print('Failed to set resolution for\n  "%s":"%s":\n    Make sure laser is online and try again manually.'%(devType,devices[key][devType]))
                    elif devType == 'ps4000a':
                        # create picoscope instance
                        self.dev[key] = ps4000a.PS4000a(serialNumber=devices[key][devType])
                    elif devType == 'LRQ600':
                        # create instance for the Zaber xy-stage
                        self.dev[key] = LRQ600.LRQ600(devices[key][devType])
                        # set stage units
                        self.dev[key].setUnits('mm')
                    elif devType == 'lockIn':
                        if devices[key][devType] == 'marc':
                            # create lockIn instance
                            self.dev[key] =  lockIn.lockIn()
                        else:
                            if self.printExceptions:
                                print('LockIn "%s":"%s" not known'%(devType,devices[key][devType]))
                    elif devType == 'lcAO4':
                        # create lucid Control AO4 instance
                        self.dev[key] = lcAO4.LCAO4(serialNr=int(devices[key][devType]))
                    elif devType == 'numatoLabRL002':
                        # create numato Lab RL002 relay instance
                        self.dev[key] = rl002 = numatoLabRL002.RL002(name=devices[key][devType])
                except Exception, e:
                    if self.printExceptions:
                        print('Failed to connect to device \n  "%s":"%s":\n    %s'%(devType,devices[key][devType],str(e)))
        
    
    def __delete__(self):
        """
        Delete instance and make sure to free ports by calling close methods on children.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        ---
        
        """
        self.closeAll()
    
    def prepareForRun(self):
        """
        Prepare for a measurement run. This method is called by the mother class when calling runExperiment. 
        Its purpose is mainly to free ports which need to be opened by the subsequently called python program, but it can be used for further tasks as well.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        ---
        
        """
        self.closeAll()
    
    def closeAll(self):
        """
        Close all connected devices.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        ---
        
        """
        for key in self.dev.keys():
            try:
                self.dev[key].close()
            except Exception, e:
                if self.printExceptions:
                    print("Failed to close device %s: %s"%(key,str(e)))
    
