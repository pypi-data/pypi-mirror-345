import zaber.serial as zs
import numpy as np
import time

class LRQ600():
    """
    Class to handle the Zaber LRQ600 XYZ stage.
    
    Access is given through serial port, disguised through and serial to USB adapter.
    
    
    """
    
    # dictionary translation userCommands (keys) to Zaber commands (values)
    cmd = { "home"      : "home",
            "pos"       : "/get pos",
            "moveTo"    : "/move abs ",
            "moveRel"   : "/move rel ",
            "reset"     : "system reset",
            "stop"      : "stop"}
    
    def __init__(self,port,invert=[False,True,False],units='mm'):
        """
        Initializes object with default configuration.
        
        https://www.zaber.com/support/?tab=Device+Settings&device=X-LRQ600BP-E01&peripheral=N/A&version=6.28&protocol=ASCII
        
        Parameters
        ==========
        
        port: string
          Port where the stage is attached to. E.g. "/dev/tty.usbserial-A104BY60"
        
        invert: list
          On which axis to invert the direction.
        
        units: string
          Units used for position. Available are: 'um', 'mm', 'm', and 'kpc'. Standard is 'mm'.
        
        Returns
        =======
        
        ---
        
        """
        # open the connection to the stage
        self.port = zs.AsciiSerial(port)
        # the working origin of the coordinate system with respect to the homing position
        # the origin is always saved in terms of the absolute stage coordiante system
        self.origin = np.zeros(3)
        # rotation angle of coordinate system in xz-plane
        self.csAngle = 0
        # initialize scale variable
        self.scale = 1
        # alowed units to be chosen
        self.availableUnits = ['kpc','m','mm','um']
        # set units and scale
        self.setUnits(units)
        # step size of the stages
        self.microstepSize = 0.49609375e-6
        # set origin of coordinate system
        self.origin = np.array([0,0,0])
        # axis identifiers (Adjust to refelct how they are wired up)
        self.zAxis = 1
        self.xAxis = 2
        self.yAxis = 3
        self.invert = invert
        # create devices to use "sugar" methods
        self.xDev = zs.AsciiDevice(self.port, self.xAxis)
        self.yDev = zs.AsciiDevice(self.port, self.yAxis)
        self.zDev = zs.AsciiDevice(self.port, self.zAxis)
        # original limit u'1212472'
        # wait with execution of new command until old one is completed
        self.waitTillCompleted = True
    
    def __delete__(self):
        self.port.close()
    
    ####################################################################################
    # "Internal methods"
    
    # Method to give feedback to user
    def printMsg(self,msg):
        """
        Internal method.
        
        Prints a message obtained from the communication with the Zaber device.
        
        Parameters
        ==========
        
        msg: string
          Message to be printed
        
        Returns
        =======
        
        ---
        
        """
        print("Zaber LRQ 600: "+msg)
    
    # Check whether the reply of a requested command is positive
    def checkCommandSucceeded(self,reply):
        """
        Internal method.
        
        Checks the return flag of the Zaber message to see whether execution of command succeeded or not.
        
        Parameters
        ==========
        
        reply: Zaber reply format
          Reply obtained from the Zaber device.
        
        Returns
        =======
        
        Boolean. True if successful, False otherwise.
        
        """
        if reply.reply_flag != "OK": # If command not accepted (received "RJ")
            self.printMsg("Danger! Command rejected because: {}".format(reply.data))
            return False
        else: # Command was accepted
            return True
    
    # return distance in microsteps
    def toMicrosteps(self,dist):
        """
        Internal method.
        
        Converts a distance to microsteps. The stage uses always microsteps. One microstep is self.microstepSize meters.
        
        Parameters
        ==========
        
        dist: num
          Distance in self.units.
        
        Returns
        =======
        
        Number of microsteps.
        
        """
        return dist*self.scale/self.microstepSize
    
    # return microsteps in distance
    def toDistance(self,microsteps):
        """
        Internal method.
        
        Converts a microsteps to distance in units of self.units. The stage uses always microsteps. One microstep is self.microstepSize meters.
        
        Parameters
        ==========
        
        microsteps: int
          Number of microsteps.
        
        Returns
        =======
        
        Distnace in units of self.units.
        
        """
        return microsteps*self.microstepSize / self.scale
    
    # send a command to the stages
    def execute(self,axis,content):
        """
        Internal method.
        
        Executes a command.
        
        Parameters
        ==========
        
        axis: int
          Axis specifier. Has to be either self.xAxis, self.yAxis, or self.zAxis
        
        content: string
          The command to be executed. Use the self.cmd command dictionary as a help to find the correct command strings. 
          Use, e.g., content = self.cmd["home"].
        
        Returns
        =======
        
        [success,reply]:
          Success is a boolean which contains the success flag obtained from the Zaber device.
          Reply is the full reply from the Zaber device.
        """
        
        if self.waitTillCompleted:
            if axis == self.xAxis:
                self.xDev.poll_until_idle()
            elif axis == self.yAxis:
                self.yDev.poll_until_idle()
            elif axis == self.zAxis:
                self.zDev.poll_until_idle()
        self.port.write(zs.AsciiCommand(axis, content))
        reply = self.port.read()
        success = self.checkCommandSucceeded(reply)
        return [success,reply]
    
    def rotMat(self,angle):
        """
        Internal method.
        
        Rotation matrix to rotate the xz-coordinate system 
        
        Parameters
        ==========
        
        angle: num
          Angle by which the coordinate system is be rotated.
        
        Returns
        =======
        
        2x2 np.array containing the rotation matrix.
        
        """
        return np.array([[np.cos(angle),0,np.sin(angle)],[0,1,0],[-np.sin(angle),0,np.cos(angle)]])
    
    # get the stage coordinates from a position in user coordinate system
    def getStageCoords(self,pos):
        """
        Internal method.
        
        Get the stage coordinates from a position in user coordinate system.
        The stage coordinate system is the absolute coordinate system of the stage with repsect to its home position. The stage coordinate system is not rotated.
        The user coordinate system is shifted by self.origin with repsect to the home position of the stage coordinate system and it is rotated by an angle self.csAngle with repsect to the stage coordinate system.
        
        Parameters
        ==========
        
        pos: list or np.array with 2 entries
          The two entries encode x and y position to be converted.
        
        Returns
        =======
        
        np.array with 2 entries:
          The two entries encode x and y position in the stage coordinate system.
        
        """
        return np.dot(self.rotMat(-self.csAngle),np.array(pos))+self.origin
    
    # get the user coordinates from a position in stage coordinate system
    def getUserCoords(self,pos):
        """
        Internal method.
        
        Get the user coordinates from a position in stage coordinate system.
        The stage coordinate system is the absolute coordinate system of the stage with repsect to its home position. The stage coordinate system is not rotated.
        The user coordinate system is shifted by self.origin with repsect to the home position of the stage coordinate system and it is rotated by an angle self.csAngle with repsect to the stage coordinate system.
        
        Parameters
        ==========
        
        pos: list or np.array with 2 entries
          The two entries encode x and y position to be converted.
        
        Returns
        =======
        
        np.array with 2 entries:
          The two entries encode x and y position in the user coordinate system.
        
        """
        return np.dot(self.rotMat(self.csAngle),np.array(pos)-self.origin)
    
    ####################################################################################
    # "User" methods
    
    def rotateCoordSysToRefPoint(self,pos):
        """
        Rotate coordinate xz-system around its current origin such that the angle between the line defined by the origin and the point pos with respect to the x-axis
        is the same angle as the one between the line defined by the origin and the current posotion of the stage and the x-axis.
        
        Use this method after setting the origin of the coordinate system to adjust the angle of the coordinate system by telling the stage at which point it currently is supposed to be.
        Therefore, this method changes self.csAngle which specifies the rotation angle of the current coordinate system.
        
        Parameters
        ==========
        
        pos: list or np.array with 2 entries
          The two entries encode x and y position to be converted.
        
        Returns
        =======
        
        [origin,csAngle]
          Origin is a 2-entry np.array specifying the origin and csAngle is the rotation angle in rad.
          The origin is not changed by the method call and is return for completness only.
        
        """
        if pos[0]**2 > 0:
            desiredAngle = np.mod((np.arctan(pos[2]/pos[0])-(np.sign(pos[0])-1)*np.pi/2),2*np.pi)
        else:
            desiredAngle = np.mod(np.sign(pos[2])*np.pi/2,2*np.pi)
        actPos = self.getPos()
        if actPos[0]**2 > 0:
            actAngle = np.mod((np.arctan(actPos[2]/actPos[0])-(np.sign(actPos[0])-1)*np.pi/2),2*np.pi)
        else:
            actAngle = np.mod(np.sign(actPos[2])*np.pi/2,2*np.pi)
        return self.rotateCoordSys(actAngle-desiredAngle)
    
    # rotate coordiante system
    def rotateCoordSys(self,angle):
        """
        Rotate xz-coordinate system around its current origin by angle.
        
        This method changes self.csAngle by angle which specifies the rotation angle of the current coordinate system.
        
        Parameters
        ==========
        
        angle: num
          Rotation angle in rad.
        
        Returns
        =======
        
        [origin,csAngle]
          Origin is a 2-entry np.array specifying the origin and csAngle is the rotation angle in rad.
          The origin is not changed by the method call and is return for completness only.
        
        """
        self.csAngle = np.mod(self.csAngle+angle,2*np.pi)
        return [self.origin,self.csAngle]
    
    # set working units
    def setUnits(self,units):
        """
        Sets the units of the coordinate system.
        
        Parameters
        ==========
        
        units: string
          Unit specifier. Allowed are the entries of self.availableUnits.
        
        Returns
        =======
        
        ---
        
        """
        self.units = units
        newOrigin = self.origin*self.scale
        if units not in self.availableUnits:
            print("Chosen units are not supported. Switch to milimeters in stead.")
        else:
            if units == 'um':
                self.scale = 1e-6
            elif units == 'mm':
                self.scale = 1e-3
            elif units == 'm':
                self.scale = 1
            elif units == 'kpc':
                self.scale = 3.0857e19
        self.origin = newOrigin/self.scale
    
    def waitTillReady(self):
        """
        Wait until the stage (both axes) finished the execution of their current command.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        ---
        
        """
        self.xDev.poll_until_idle()
        self.yDev.poll_until_idle()
        self.zDev.poll_until_idle()
        
    
    # do homing
    def home(self):
        """
        Perform homing. Resets self.origin.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        ---
        
        """
        [successy,reply] = self.execute(self.yAxis,self.cmd["home"])
        self.yDev.poll_until_idle()
        [successx,reply] = self.execute(self.xAxis,self.cmd["home"])
        [successz,reply] = self.execute(self.zAxis,self.cmd["home"])
        
        if not successx or not successy or not successz:
            self.printMsg("Homing failed!")
        self.origin = np.array([0,0,0])
        
    
    # return current position
    def getPos(self):
        """
        Get the current position from the stages.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        2-entry np.array
          Contains the current x and y position of the stage in units of self.units.
        
        """
        [successx,replyx] = self.execute(self.xAxis,self.cmd["pos"])
        [successy,replyy] = self.execute(self.yAxis,self.cmd["pos"])
        [successy,replyz] = self.execute(self.zAxis,self.cmd["pos"])
        if not successx or not successy:
            self.printMsg("Could not get position!")
        else:
            xx=self.toDistance(int(replyx.data))
            if self.invert[0]:
                xx=0.601/self.scale-xx
            yy=self.toDistance(int(replyy.data))
            if self.invert[1]:
                yy=0.601/self.scale-yy
            zz=self.toDistance(int(replyz.data))
            if self.invert[2]:
                zz=0.601/self.scale-zz
            return self.getUserCoords(np.array([xx,yy,zz]))
    
    # move to absolute value pos. Pos is with respect to the current coordinate system.
    def moveTo(self,pos):
        """
        Move to the absolute position pos. Works with respect to current coordinate system.
        
        Parameters
        ==========
        
        pos: 3-value array or list
          x and y and z position of the desired position in units of self.units.
        
        Returns
        =======
        
        ---
        
        """
        coords = self.getStageCoords(np.array(pos))
        xx=coords[0]
        if self.invert[0]:
            xx=0.601/self.scale-xx
        yy=coords[1]
        if self.invert[1]:
            yy=0.601/self.scale-yy
        zz=coords[2]
        if self.invert[2]:
            zz=0.601/self.scale-zz
        
        current=self.getPos()
        
        
        if (abs(current[0]-pos[0])*self.scale > 2e-6 or abs(current[2]-pos[2])*self.scale > 2e-6):
            [successf,reply] = self.execute(self.yAxis,self.cmd["moveTo"]+"%d"%self.toMicrosteps(0))
            self.yDev.poll_until_idle()
            [successx,reply] = self.execute(self.xAxis,self.cmd["moveTo"]+"%d"%self.toMicrosteps(xx))
            [successz,reply] = self.execute(self.zAxis,self.cmd["moveTo"]+"%d"%self.toMicrosteps(zz))
            self.xDev.poll_until_idle()
            self.zDev.poll_until_idle()
            time.sleep(4)
        else:
            successx=True
            successz=True
            successf=True
        
        [successy,reply] = self.execute(self.yAxis,self.cmd["moveTo"]+"%d"%self.toMicrosteps(yy))
        self.yDev.poll_until_idle()
        
        if not successx or not successy or not successz or not successf:
            self.printMsg("Could not nove to requested position!")
    
    
    # select a coordinate system
    def setCoordSys(self,key='abs',origin=np.zeros(3)):
        """
        Choose the current coordinate system. Choices available are:
          - reset: resets the coordinate system to the absolute coordinate system of the stage. The origin should then correspond to the homing position and the rotation angle is set to zero.
          - abs  : resets the origin of the coordiante system to the absolute origin of the stage. The origin should then correspond to the homing position. The rotation angle remains unchanged.
          - rel  : move the origin of the current coordinate system by origin.
          - here : move the origin of the coordinate system to the current position of the stage.
        
        Parameters
        ==========
        
        key: string
          Specifier of the coordiante system. Available are 'reset', 'abs', 'rel', and 'here'.
        
        origin: 3-value list or np.array
          Only used in mode 'rel'. Defines the relative distance in units of self.units by which the origin of the coordinate system should be changed.
         
        Returns
        =======
        
        [origin,csAngle]
          Origin is a 2-entry np.array specifying the origin and csAngle is the rotation angle in rad.
        
        """
        if key == 'reset':
            self.origin = np.zeros(3)
            self.csAngle = 0
        # coordinate system with respect to absolute reference point
        elif key == 'abs':
            self.origin = np.zeros(3)
        # set reference point of coordinate system to origin
        elif key == 'rel':
            self.origin = self.getStageCoords(origin)
        # set reference point of coordinate system current position
        elif key == 'here':
            self.origin = self.getStageCoords(self.getPos()-origin)
        else:
            self.printMsg("Unkown coordinate system. Use 'reset','abs', 'rel' or 'here' key.")
        return [self.origin,self.csAngle]
    
    # reset drives <-> as replugged
    def reset(self):
        """
        Triggers the reset command of the stage. Is supposed to be equivalent to a replug of the stages according to Zaber.
        
        Parameters
        ==========
        
        ---
         
        Returns
        =======
        
        ---
        
        """
        [successx,reply] = self.execute(self.xAxis,self.cmd["reset"])
        [successy,reply] = self.execute(self.yAxis,self.cmd["reset"])
        [successz,reply] = self.execute(self.zAxis,self.cmd["reset"])
        if not successx or not successy or not successz:
            self.printMsg("Could not reset drives!")
    
    # stop motion of drives
    def stop(self):
        """
        Stop the current motion.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        ---
        
        """
        [successx,reply] = self.execute(self.xAxis,self.cmd["stop"])
        [successy,reply] = self.execute(self.yAxis,self.cmd["stop"])
        if not successx or not successy:
            self.printMsg("Could not stop drives!")
    
    # close port
    def close(self):
        """
        Close the serial communication port
        
        Parameters
        ==========
        
        ---
         
        Returns
        =======
        
        ---
        
        """
        self.port.close()