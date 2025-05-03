import requests
import json
import os
import platform

class IDS3010():
    """
    Class to simplify the communication with the attocube IDS3010. 
    
    Implements some of the commands offered by the webserver of the device. The communication is based on the JSON protocol. 
    
    """
    def __init__(self, url):
        """
        Initilaze attocube system IDS3010, identified by its url.
        
        Parameters
        ==========
        
        url: string
          Url how to reach the system. E.g. "http://192.168.1.1:8080".
        
        Returns
        =======
        
        ---
        
        """
        self.resolution = None
        self.url = url
        # get ip address from url
        self.ip = url.split(":")[1].split("//")[1]
    
    def serverAvailable(self):
        """
        Check reachability of the systems webserver using ping.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        boolean:
          True if available. False otherwise.
        
        """
        # check availability
        if platform.system() == "Windows":
            response = os.system("ping -n 1 " + self.ip)
        else:
            response = os.system("ping -c 1 " + self.ip)
        if response == 0:
            return True
        return False
    
    def getResolution(self):
        """
        Get the resolution of sin/cos and AquadB in pm/90 degrees.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        res: int32
          Resolution: 1 to 65535.
        
        """
        if not self.serverAvailable():
            print("IDS3010 not available")
            return
        url = self.url+"/api/json"
        headers = {'content-type': 'application/json'}

        # Example echo method
        payload = {
            "method": "com.attocube.ids.realtime.getResolutionSinCos",
            "params": [],
            "jsonrpc": "2.0",
            "id": 0,
        }
        response = requests.post(
            url, data=json.dumps(payload), headers=headers).json()
        try:
            res = response['result'][0]
            self.resolution = res
        except Exception:
            print("Error in communication with interferometer. Got back:")
            print(response)

    def getCurrentMode(self):
        """
        Get the current mode of operation.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        Description: string
          A short description of the current mode: "system idle", "measurement starting", "measurement running", "optics alignment starting", "optics alignment running", "pilot laser enabled".
        
        """
        if not self.serverAvailable():
            print("IDS3010 not available")
            return
        url = self.url+"/api/json"
        headers = {'content-type': 'application/json'}

        # Example echo method
        payload = {
            "method": "com.attocube.ids.system.getCurrentMode",
            "params": [],
            "jsonrpc": "2.0",
            "id": 0,
        }
        response = requests.post(
            url, data=json.dumps(payload), headers=headers).json()
        try:
            res = response['result'][0]
            return res
        except Exception:
            print("Error in comunication with interferometer. Got back:")
            print(response)
        return None

    def doMethod(self,method,params=[]):
        """
        Call an arbitrary method via JSON. 
        
        Parameters
        ==========
        
        method: string
          Name of the method to be called. E.g. "com.attocube.ids.system.getCurrentMode". See manual for available methods.
        
        params: list
          List of parameters for given method.
        
        Returns
        =======
        
        result: ???
          Depends on method called.
        
        """
        if not self.serverAvailable():
            print("IDS3010 not available")
            return
        url = self.url+"/api/json"
        headers = {'content-type': 'application/json'}

        # Example echo method
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        response = requests.post(
            url, data=json.dumps(payload), headers=headers).json()
        try:
            res = response['result']
            return res
        except Exception:
            print("Error in comunication with interferometer. Got back:")
            print(response)
        return None

    
    def getContrast(self,axis):
        """
        Returns the contrast of the signal (ratio signal maximum to signal minimum) in per mill.
        
        Parameters
        ==========
        
        axis: int: 0,1,2
          Which of the three axes.
        
        Returns
        =======
        
        result: int
          Contrast in per mill.
        
        """
        if not self.serverAvailable():
            print("IDS3010 not available")
            return
        url = self.url+"/api/json"
        headers = {'content-type': 'application/json'}

        # Example echo method
        payload = {
            "method": "com.attocube.ids.adjustment.getContrastInPermille",
            "params": [axis],
            "jsonrpc": "2.0",
            "id": 0,
        }
        response = requests.post(
            url, data=json.dumps(payload), headers=headers).json()
        try:
            res = response['result']
            return res
        except Exception:
            print("Error in comunication with interferometer. Got back:")
            print(response)
        return None

        
    def isLaserRunning(self):
        """
        Checks whether the systems currentMode equals 'measurement running'.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        bool:
          True if current mode is 'measurement running'. False otherwise.
        
        """
        return 'measurement running' == self.getCurrentMode()