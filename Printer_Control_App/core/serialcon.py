
import serial
from serial import (Serial, SerialException)  

#this is designed to read form a arduino serial port
#Class for any serial connection (e.g. connection to conductance meter)
class SerialConnection(object):
    """connects to serial port and sends and receives data

    Args:
        object (_): 

    attributes:
        _type_ (str): type of serial connection
        status (bool): status of serial connection
        port (str): port to connect to
        baud (int): baud rate
        ser (Serial): serial object
        
    Methods:

    """
    instances = [] # list of all instances of this class
    def __init__(self):
        self.type="unknown"
        self.status=False

        # Checks connection with serial port
        
        #TODO: make sure correct port is called
    def connect(self, port, baud):
        """connects to serial port specified by port and baud rate specified by baud


        Args:
            port (str): port to connect to
            baud (int): baud rate
        """
        self.port=port #port
        self.baud=baud #baud rate
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=2) #setting up serial connection: open port
            self.status=True
            print("connected to ser")
        except:
            print("ser not created")
 
    
    def checktype(self,line):
        """
        checks the type of the serial connection

        Args:
            line (int): _description_
        """
        for i in range(line):
            self.send('t\r\n')  #send t to get type from the arduino
            typ=self.read()
        try:
            self.type=typ.decode("utf-8")
        except:
            self.type=typ

    def send(self,msg):
        """sends message to serial port

        Args:
            msg (str): message to send
        """
        try:
            msg=msg.encode()
            self.ser.write(msg)
        except:
            print("sending error")

    def read(self):
        """reads message from serial port


        """
        try:
            msg = self.ser.readline()
            return msg
        except:
            msg=1
            print("No line to read")
            return msg
            

    def sync(self):
        """
        sends sync message to serial port to synchronize
        likely a reset
        """
        self.send('r') #reset?
        
        
    def flush(self):##TODO: check if this is necessary remove if not
        #
        pass
        #self.ser.flushInput()
        #self.ser.flushOutput()
        #self.ser.flush()

    # Disconnects from serial port
    def disconnect(self):
        """
        disconnects from serial port can remove flush if not necessary
        """
        if self.status==True:
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.flush()
            self.ser.close()
            self.status=False

