import re
import socket 



class SocketSerialProxy:
    def __init__(self, host, port, timeout=2.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.connected = False
        # Do not connect in __init__, mimic lazy opening like PySerial

    def open(self):
        if self.isOpen():
            return
        try:
            self.sock = socket.create_connection((self.host, self.port))
            self.sock.settimeout(self.timeout)
            self.connected = True
        except socket.error as e:
            self.connected = False
            raise RuntimeError(f"Socket connection failed: {e}")

    def isOpen(self):
        return self.connected and self.sock is not None

    def write(self, command: bytes):
        if not self.isOpen():
            raise RuntimeError("Socket is not open")
        self.sock.sendall(command)

    def flush(self):
        pass  # sockets don’t buffer at the Python level

    def readline(self):
        if not self.isOpen():
            raise RuntimeError("Socket is not open")
        data = b''
        try:
            while not data.endswith(b'\r\n'):
                chunk = self.sock.recv(1024)
                if not chunk:
                    self.close()
                    break
                data += chunk
        except socket.timeout:
            pass
        return data

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except socket.error:
                pass
        self.sock = None
        self.connected = False


class pressureControl(object):
    """
    Class to fetch the pressure

    This class handles the communction with the RVC 300 Control unit gas regulating valves in use with an EVR 116

    Parameters
    ==========
    serialPort : str
        Name of the serial port at which the controller is hanging
    baudRate : int
        baud rate of the connection    
    """
    def __init__(self, address: str = 'blueberry-cmtqo', port : int = 27962) -> None:
        self.port = port
        self.address = address
        self.serialHandle = SocketSerialProxy(self.address, self.port)
        self.serialHandle.open()
        
        
    def openConnection(self) -> None:
        """ 
        Tries to open the serial port and checks if it was successful.

        """
        if not self.serialHandle.isOpen():
            try:
                self.serialHandle.open()
                if self.serialHandle.isOpen():
                    print("The serial connection was successfully opened.")
                else: 
                    print("The serial connection is still closed.")
            except Exception as e:
                print(f"An error occurred while opening the serial connection: {e}")
        else:
            print("The serial connection is already open.")


    def closeConnection(self) -> None:
        """ 
        Tries to close the serial port and checks if it was successful.
        
        """        
        try:
            self.serialHandle.close()
            if not self.serialHandle.isOpen():
                print("The serial connection was successfully closed.")
            else:
                print("The serial connection is still open.")
        except Exception as e:
            print(f"An error occurred while closing the serial connection: {e}")

    def getPressureSetPoint(self) -> float:
        """
        Gets the pressure set point.


        Output:
        ======
        p:  float
            pressure set point in mbar

        """
        command = self.serialHandle.write(b'PRS?\r\n')
        self.serialHandle.flush()

        response = self.serialHandle.readline()
        pressure = response.decode()

        # extract number
        match = re.match(r"PRS=([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)([a-zA-Z]+)", pressure)
        if match is not None:
            return float(match.group(1))

        else:
            print(f'Error during measurement at time {t[k]}s: Pressure Set Point could not be retrieved.')
            return None

    def closeValve(self) -> None:
        """ 
        Closes the valve 
        """
        unit=self.getUnit().split("=")[1].strip()
        command={'mbar':f'FLO=4.99E-06\r\n','Pa':f'FLO=4.99E-04\r\n','Torr':f'FLO=3.74E-06\r\n'}
        command_bytes=command[unit].encode('utf-8')
        self.serialHandle.write(command_bytes)
        self.serialHandle.flush()
        response = self.serialHandle.readline()
        print(f"Flow set to: {response.decode()}")
    
    def setPressureSetPoint(self, p: float = 5.00E-04) -> None:
        """ 
        Sets the pressure set point and checks if it is within the range of the connected pressure sensor TPR 280.

        Input:
        ======
        p : float formatted as x.xxE-xx
            pressure set point in mbar

        """
        if p < 5.00E-04 or p > 1.00E+03: # mbar
            return "Error: pressure set point p must be between 5.00E-04 and 1.00E+03 mbar."
                    
        command = f'PRS={p:3.2E}\r\n'  
        command_bytes = command.encode('utf-8')

        self.serialHandle.write(command_bytes)
        self.serialHandle.flush()

        response = self.serialHandle.readline()
        print(f"Pressure Set Point set: {response.decode()}")

    
    def getPressure(self) -> float:
        """
        Returns the pressure in mbar from the connected pressure sensor.

        Returns
        =======
        float
            Pressure in mbar, or None if parsing fails.
        """
        self.serialHandle.write(b'PRI?\r\n')
        self.serialHandle.flush()

        response = self.serialHandle.readline()
        pressure = response.decode()

        # extract number
        match = re.match(r"PRI=([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)([a-zA-Z]+)", pressure)
        if match is not None:
            return float(match.group(1))

        else:
            print(f'Error during measurement: Pressure Set Point could not be retrieved.')
            return None
        
    
    def getUnit(self) -> str:
        """ 
        Returns the current unit in which pressure is measured (e.g. 'mbar', 'Pa', 'torr').

        """            
        self.serialHandle.write(b'UNT?\r\n')
        self.serialHandle.flush()
        response = self.serialHandle.readline()
        print(f"Current Unit: {response.decode()}")
        return response.decode()
    
    def getValvesPosition(self) -> str:
        """ 
        Returns the current position of the valve.

        """            
        self.serialHandle.write(b'VAP?\r\n')
        self.serialHandle.flush()
        response = self.serialHandle.readline()
        print(f"Position of Valve: {response.decode()}")
        return response.decode()
    
    def getValvesTemperature(self) -> str:
        """ 
        Returns the current temperature of the valve.

        """
        self.serialHandle.write(b'VAT?\r\n')
        self.serialHandle.flush()
        response = self.serialHandle.readline()
        print(f"Temperature of Valve: {response.decode()}")
        return response.decode()
    
    def getValvesStatus(self) -> str:
        """ 
        Returns the current status of the valve.

        """      
        command = self.serialHandle.write(b'VAS?\r\n')
        self.serialHandle.flush()
        response = self.serialHandle.readline()
        print(f"Status of Valve: {response.decode()}")  
        return response.decode()

    def getValvesVersion(self) -> str:
        """ 
        Returns the current version of the valve.

        """      
        self.serialHandle.write(b'VAV?\r\n')
        self.serialHandle.flush()
        response = self.serialHandle.readline()
        print(f"Version of Valve: {response.decode()}")  
        return response.decode()
    
    
    def setRegulator(self, N: int = 0) -> str:
        """ 
        Sets the mode of the regulator.

        RVC 300 has automatic regulator types (PI) from Auto 1 to Auto 99 and PID.
        Auto for a quick process optimization
        PID for a precise regulation to the desired set point and rapid reaction.

        Input:
        ======
        N : integer formatted as xx
            PI-Regulator: N = 1 ... 99 (1 = slow, 99 = fast)
            PID-Regulator: N = 0

        """
    
        if N < 0 or N > 99:
            return "Error: N must be between 0 and 99."
        
        command = f'RAS={N:02}\r\n'
        command_bytes = command.encode('utf-8')

        self.serialHandle.write(command_bytes)
        self.serialHandle.flush()

        response = self.serialHandle.readline()

        print(f"The regulator has been set: {response.decode()}")  
        return response.decode()

        
    def getRegulator(self) -> int:
        """
        Returns the mode of the regulator.

        Output:
        ======
        mode:   int
                mode of the regulator
                PI-Regulator: N = 1 ... 99 (1 = slow, 99 = fast)
                PID-Regulator: N = 0

        """
        self.serialHandle.write(b'RAS?\r\n')
        self.serialHandle.flush()

        response = self.serialHandle.readline()
        mode = response.decode()

        print(f"Current Regulator: {mode}")

        match = re.match(r"RAS=\s*([0-9]+)", mode)

        return int(match.group(1))
    
    def setPIDParameters(self, P: float = 001.0, I: float = 0000.3, D: float = 0000.0) -> None:
        """ 
        Sets the PID control parameters.
        The regulator must be set to 0 for it to be in PID mode.

        Input:
        =======
        P : float
            Amplification factor between 0.1 and 100.0
        I : float
            Reset time (Tn) between 0.0 and 3600.0 seconds
        D : float
            Derivative time (Tv), rate time between 0.0 and 3600.0 seconds
        """
    
    
        if not (0.1 <= P <= 100.0):
            raise ValueError("Amplification factor P must be between 0.1 and 100.0.")
    
        if not (0.0 <= I <= 3600.0):
            raise ValueError("Reset time I (Tn) must be between 0.0 and 3600.0 seconds.")
        
        if not (0.0 <= D <= 3600.0):
            raise ValueError("Derivative time D (Tv) must be between 0.0 and 3600.0 seconds.")
    
   
        command_p = f'RSP={P:05.1f}\r\n' 
        command_i = f'RSI={I:06.1f}\r\n' 
        command_d = f'RSD={D:06.1f}\r\n' 

    
        command_p_bytes = command_p.encode('utf-8')
        command_i_bytes = command_i.encode('utf-8')
        command_d_bytes = command_d.encode('utf-8')

    
        self.serialHandle.write(command_p_bytes)
        self.serialHandle.flush()
        response_p = self.serialHandle.readline()

        self.serialHandle.write(command_i_bytes)
        self.serialHandle.flush()
        response_i = self.serialHandle.readline()

        self.serialHandle.write(command_d_bytes)
        self.serialHandle.flush()
        response_d = self.serialHandle.readline()

        print(f"Amplification (Kp) set: {response_p.decode().strip()}")
        print(f"Reset time (Tn) set: {response_i.decode().strip()}")
        print(f"Derivative time (Tv) set: {response_d.decode().strip()}")


    def getPIDParameters(self) -> tuple[float, float, float]:
        """ 
        Returns the current PID control parameters.
        The regulator must be set to 0 for it to be in PID mode.

        Output:
        ======
        Kp: float
            Amplification
        
        Tn: float
            Reset Time

        Tv: float    
            Derivative Time
        """
        command_p = f'RSP?\r\n' 
        command_i = f'RSI?\r\n' 
        command_d = f'RSD?\r\n' 

        command_p_bytes = command_p.encode('utf-8')
        command_i_bytes = command_i.encode('utf-8')
        command_d_bytes = command_d.encode('utf-8')

        self.serialHandle.write(command_p_bytes)
        self.serialHandle.flush()
        response_p = self.serialHandle.readline()

        self.serialHandle.write(command_i_bytes)
        self.serialHandle.flush()
        response_i = self.serialHandle.readline()

        self.serialHandle.write(command_d_bytes)
        self.serialHandle.flush()
        response_d = self.serialHandle.readline()

        print(f"Current Amplification (Kp): {response_p.decode().strip()}\n"
              f"Current Reset Time (Tn): {response_i.decode().strip()}\n"
              f"Current Derivative Time (Tv): {response_d.decode().strip()}\n")
        
        match_p = re.match(r"RSP=\s*([0-9]+\.[0-9]+)", response_p.decode())
        match_i = re.match(r"RSI=\s*([0-9]+\.[0-9]+)", response_i.decode())
        match_d = re.match(r"RSD=\s*([0-9]+\.[0-9]+)", response_d.decode())
        
        return float(match_p.group(1)), float(match_i.group(1)), float(match_d.group(1))
    
    def flush(self):
        self.serialHandle.flush()
        
    def __delete__(self):
        self.serialHandle.closeConnection()
