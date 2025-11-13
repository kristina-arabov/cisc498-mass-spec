import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
import time
import queue as Queue


#Class/Thread to process data from conductance meter
#Uses "connection" as argument which is an object of SerialConnection
#and flag argument in order to stop thread loop

#Outputs two queue with time and conductance values

#signalmessage to output messageboxes
class ConThread(QtCore.QThread):
    print("Conductance Instance generated")
    signalmessage=QtCore.pyqtSignal(str,str) #signal that takes a string and a string as argument
    
    def __init__(self,parent=None):
        super(ConThread,self).__init__(parent)
        self.flag=False
        self.setTerminationEnabled=True #may be broken
        self.datapoint=[] #datapoint to be put in queue
        self.conductance_queue = Queue.Queue()
        self.values=[]      
        self.capDecode = 0#array with times and conductance values

    # Tries to start the conductance
    def run(self):
        """
        this tries to start the conductance thread and checks if the connection is correct
        """
        print("started con thread")
        try:
            self.flag=self.checkcon()
            time.sleep(1)
            self.connection.flush()
            print('flushed')
            self.startThr=int(round(time.time()*1000))
        except:
            self.flag=False

        while self.flag:
            try:
                self.readingLoop()
            except:
                print("Conductance Readout Error")
                self.flag=False 

    # Checks connection for the conductance
    def checkcon(self):
        """Checks the status of the serial connection and its type.

    Returns:
        bool: True if the connection is open and the type is correct,
              False otherwise.
    """
        print("check con start")
        if (self.connection.ser.is_open==True):#checks if serial connection is open
            print("check con")
            if ((self.connection.type=='c\r\n')& (self.connection.ser.is_open==True)): #where do i find connection type?
                return True
            else:
                self.signalmessage.emit("connectionWrong","w")
                return False
        else:
            self.signalmessage.emit("connectionErr","w")
            return False

    def readingLoop(self):
        """reads the conductance value from the serial connection and puts it in the queue
        
        creates datapoint with time and conductance value for graphing then puts in queue to be graphed
        """
        if self.datapoint is not None and self.conductance_queue.qsize() < 2:
            self.connection.sync() #send request ie 'r'
            #add some wait for this
            cap=self.connection.read()#reads the conductance value
            self.capDecode= int(cap.decode("utf-8")) #to decode the value
            timenew = int(round(time.time()*1000))-self.startThr #time in ms    
            self.datapoint=[timenew,self.capDecode] #creates a datapoint
            self.connection.flush()
            self.conductance_queue.put(self.datapoint)
        else:
            time.sleep(self.ratems/1000)

    def plotrange(self):
        """
        sets the refresh rate and range of the graph and range of the graph
        
        """
        self.rangesec=3
        print(self.rangesec)
        try:
            self.refreshrate=self.values[-1][0]-self.values[-2][0]
        except:
            self.refreshrate=30

    # Exits conductance
    def stop(self):
        
        """stops the conductance thread"""
        self.terminate()
