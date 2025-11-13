import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
import time
#from core import serialcon
import queue as Queue


class Pump_control(QtCore.QThread):
    print("q")
    def __init__(self,parent=None):
        
        """
        initalizes the pump control class
        """
        super(Pump_control,self).__init__(parent)
        self.connected=False

        self.flowrate=None
        self.volume=None 
        self.syringed=None

        self.mode=None

        self.qsampling=None
        self.qdwell=None

        self.Connection=None
        self.ready=False
        self.cmdqueue=Queue.Queue() #queue of commands to be sent

        self.running=False

        self.initialized=False
        #hexw2 2 0 initilize units ul and ul/min and infusion mode, start, stop, pause,


    def run(self):
        """
        starts the pump control thread
        """
        self.cmdqueue.put("hexw2 2 0\r\n")       #initialize units 2:µL/min and 0: infusion
        while self.Connection.status:
            self.send()
            output=self.Connection.read() #read output from pump
            outputdec=output.decode() #decode output
            #print(outputdec)
            if outputdec=='>':
                self.ready=True
                print("ready")
            if outputdec.find("set diameter =")!=-1: #check if diameter is set
                print('init done')
                self.initialized = True

    def setflowrate(self,q):
        """changes the flowrate of the pump

        Args:
            q (str): flowrate in µL/min... 
        """
        if self.Connection.status:
            self.flowrate=q
            cmd="set rate "+self.flowrate+"\r\n"
            print("flowrate changed"+self.flowrate)
            self.cmdqueue.put(cmd)

    def setvolume(self,v):
        """send volume to pump

        Args:
            v (int): volume in µL
        """
        ###NOT WORKING
        if self.Connection.status:
            vul=int(v)*1000 #convert to µL
            self.volume=vul
            cmd="set volume 10000\r\n" 
            self.cmdqueue.put(cmd) #send command to pump

    def setsyringed(self,d):
        """set diameter of syringe

        Args:
            d (int): diameter of syringe units should be mm
        """
        if self.Connection.status:
            self.syringed=d #set diameter of syringe
            cmd="set diameter "+self.syringed+"\r\n"
            self.cmdqueue.put(cmd)#send command to pump

    # Starts connection to pump
    def startpump(self):
        """
        starts the pump
        """
        if self.Connection.status and self.running==False:
            self.Connection.send("start\r\n")
            self.running=True

    # Stops connection to pump
    def stoppump(self):
        """
        stops the pump
        """
        if self.Connection.status and self.running==True:
            self.Connection.send("stop\r\n")
            self.running=False

    def send(self):
        """
        send commands to pump from queue
        """
        if self.ready==True and not self.cmdqueue.empty() and self.Connection.status:
            cmd=self.cmdqueue.get()
            self.Connection.send(cmd)
            self.ready=False




