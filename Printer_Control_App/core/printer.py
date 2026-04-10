import subprocess
import sys
import PyQt5
import time
import re
import os # to check the OS name

from PyQt5 import QtCore, QtGui, QtWidgets
import queue as Queue
import csv
# Import pandas
import pandas as pd

# Excel - sheet modules
from xlwt import Workbook
import select



class console_control(QtCore.QThread):
    """
    class for controlling the console, sending commands to the printer, and handling responses from the printer
    inherits from QThread for separate thread
    """
    get_conductance = QtCore.pyqtSignal(bool)
    print('begin')
    done_sampling = QtCore.pyqtSignal(bool)
    
    def __init__(self, parent=None):
        self.temp_queues = []
        super(console_control, self).__init__(parent) #gives access to the parent class methods
        self.flag = True
        self.prtconnect = False#port connection
        self.queue = Queue.Queue() #output queue
        self.posqueue = Queue.Queue() #position queue
        self.pos = [0, 0, 0] #position
        self.outputarr = [] #output array
        self.homed = False #home status
        self.moving = False #moving status
        self.checkmovequeue = Queue.Queue() #check move queue
        self.gcodeidx = 0 #gcode index
        self.gcodefile = False #gcode file status
        self.line = None #line
        self.gcodelist = [] #gcode list
        self.pumpstatus = 0 #pump status

        self.cond = None
        self.con_threshold = 100 
        self.touch = False
        self.counter = 0
        # Row position for Excel-sheet
        self.row = 0

        # Column position for Excel-sheet
        self.column = 0

        # Stores G-Code Instructions
        self.gcode_instructions = []

        # Counts number of G0s occur
        self.g_zero = 0

        # Keeps track of the repeating occurrences
        # Indicates the number of times a probe lowers before it lifts itself back up (after touching something conductive)
        self.repeating_occurrences = []

        self.gcode_flag = True  # Flag for G0 appearance
        self.counter_flag = True  # Flag for G0 appearance
        self.count_occurrences = 0  # Counter for counting number of G0
        self.repeating_list = []  # Stores number of occurrences

        self.sampling_spot_y = 0  # Initialize grid size (Number of Sampling Spots Y)
        
        self.stop_sampling_flag = False  # Flag for stopping the sampling process
        
        self.pause_sampling_flag = False  # Flag for pausing the sampling process
        self.temp_queue = Queue.Queue() #temperature queue
        
        self.count = 0 #count
        self.batch = False #batch status
        self.got_pos_flag = False

        self.sampling = False
        self.relative = False

        self.xy_speed = 0
        self.z_speed = 0
        self.z_speedup = 0
     
        self.xy_acceleration = 1250 #mm/s^2
        self.z_acceleration = 400 #mm/s^2
        self.eta_list   = [] #holds ETA values
        
        self.got_conductance = False
       
        
        self.current_position = 0
        
        self.conductance_mode = False
        self.lower_threshold = 0
        
        self.last_pos = [0,0,0] #last position for paue
        
        self.response = False
    def run(self):
        """
        run the console thread, initialize the subprocess of shell, handles response
        """
        
        self.flag = True
        wrapper = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pronsole_pipe.py')
        self.sc_path = [sys.executable, '-u', wrapper]
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        self.console = subprocess.Popen(self.sc_path,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True,
                                        env=env)
        print('start console thread')
      
        
        # change this loop
        while self.flag:
    
            
            self.readloop()
        
            self.displayout()

            self.checkpos()
            
            # self.check_temp(self.line)
            # print('running')
            if self.sampling:
                self.sendgcode()
            else:
                
                self.checkmove(self.pos)

            # if 'ok T:' in self.line:
            if self.line.find('ok T:') != -1:  # after G28
                self.homed = True


            # if not self.prtconnect:
            if self.prtconnect == False:
                # if 'Printer is now online' in self.line:
                if self.line.find('Printer is now online') != -1:
                    print('printer connected')
                    self.prtconnect = True

                    time.sleep(1)
                    self.cmd("M114")
                    time.sleep(1)
                    self.cmd("M105")
                    

                    

            time.sleep(0.01)



    def readloop(self):
        """
        Read the console output and put it in the queue.
        """

        if self.queue.qsize() < 2:
            
            if sys.platform != 'win32':
                rlist, _, _ = select.select([self.console.stdout], [], [], 0.02)
                if rlist:
                    self.line = self.console.stdout.readline()
                    linestr = self.line.strip()
                    self.outputarr = [linestr]
                    self.queue.put(self.outputarr)
            else:
                self.line = self.console.stdout.readline()
                linestr = self.line.strip()
                self.outputarr = [linestr]
                self.queue.put(self.outputarr)
                
        else:
            
            print('sleep 1')
            time.sleep(1)

    
        
    def displayout(self): #TODO: remove this function

        if not self.queue.empty():
            line = self.queue.get()
            self.line = line[0]
        else:
            self.line = ""

    def checkpos(self):

        """
        this function checks the position of the printer

        Args:
            line (string): the line from the console
        """

        
        if not self.sampling:
            if self.line.find('Count') != -1:
                line = self.line.split()
                self.pos = [float(line[0][2:]), float(line[1][2:]), float(line[2][2:])]
                self.posqueue.put(self.pos)
                self.cmd("M114")
                
            if self.line.find('T:') != -1:
                line = self.line
                #line = self.line.split()

                #temp = [float(line[1][2:].split('/')[0]), float(line[2][2:].split('/')[0])]
                "ok T:160.0 /160.0 B:60.0 /60.0 T0:160.0 /160.0 @:20 B@:23 P:31.9 A:26.1"
                

                
                pattern = re.compile(r"T:(\d+\.?\d*)\s*/\s*\d+\.?\d*\s*B:(\d+\.?\d*)\s*/\s*\d+\.?\d*")
                match = pattern.search(self.line)

                if match:
                    temp = [float(match.group(1)), float(match.group(2))]
                   
                else:
                    print("No match found")
                #pattern = re.compile(r"t\s*(\d+)\s*/\s*(\d+)")

                #temp = [float(pattern.search(line[1]).group(1)), float(pattern.search(line[2]).group(1))]
                
                self.temp_queue.put(temp)
                self.cmd("M105")
           
        else:
            if self.line.find('Count') != -1:
                line = self.line.split()

                self.pos = [float(line[0][2:]), float(line[1][2:]), float(line[2][2:])]
                self.posqueue.put(self.pos)
                if self.current_position == self.pos[2] and self.conductance_mode:
                    self.response = True
                elif not self.conductance_mode:
                    self.response = True
                else:
                    self.cmd("M114")
                
            
   
        
    def checkmove(self, pos): #TODO: take out the pos arugment
        """
        Check if the printer is moving

        Args:
            pos (): unused
        """
        
        if self.checkmovequeue.qsize() > 1 :
            #check for a change in position
            oldpos = self.checkmovequeue.get()
            newpos = self.checkmovequeue.get()
            dx = newpos[0] - oldpos[0]
            dy = newpos[1] - oldpos[1]
            dz = newpos[2] - oldpos[2]
            

            if (dx == 0 and dy == 0 and dz == 0): #for conductive sampling it calculates the time so dont need to worry about moving
                self.moving = False

                self.sendgcode()
                # print("not moving")
            else:
                self.moving = True
                # print('moving')

    def sendgcode(self):
        """
        Sends G-Code instructions to the printer.

        This method exports the G-Code instructions to a plain text file and an Excel spreadsheet.
        It also computes the heights and stores them in a grid format in an Excel spreadsheet or a text file.

        Returns:
            None
        """
        
        while self.pause_sampling_flag == True:
            time.sleep(1)
            print("wating for resume")
            if self.stop_sampling_flag == True:
                
                return
            
            
        if self.gcodeidx == len(self.gcodelist) and self.gcodefile:
            print('gcode done')
            
            self.sampling = False
            
            self.done_sampling.emit(True)

            #################################
            # EXPORTING G-CODE INSTRUCTIONS #
            #################################

            # Creates a Workbook
            workbook = Workbook()

            # Creates an Excel spreadsheet
            worksheet = workbook.add_sheet("Sheet 1")

            # Opens and creates a new plain text file
            with open('G-Code_Instructions.txt', 'w') as gcode_file:

                for line in self.gcode_instructions:
                    # Writes each G-Code to the plain text file
                    gcode_file.write(line)

                    # Writes each G-Code to an Excel file
                    worksheet.write(self.row, self.column, line)

                    # Increments the count for row position
                    self.row += 1

            #########################
            # OPTION #1 - Text File #
            #########################

            # Closes the plain text file
            #gcode_file.close() 

            ########################################
            # OPTION #2 - Excel Spreadsheet (File) #
            ########################################

            # Saves Excel Spreadsheet
            workbook.save("G-Code Instructions.xls")

            self.gcodeidx = 0
            self.gcodefile = False

            #################################
            # EXPORTING Z-HEIGHTS #
            #################################

            # Compares all G-Code Instructions
            for idx in self.gcode_instructions:

                # Keeps track of the number of G0s
                # Note: this indicates when the probe is lowering until it touches something conductive
                if idx[1:3] == "G0":
                    self.count_occurrences += 1
                    self.gcode_flag = True
                    self.counter_flag = True

                # If line is not G0, flag becomes False
                else:
                    self.gcode_flag = False

                # If no G0s are accounted for, flag is False
                if self.count_occurrences == 0:
                    self.counter_flag = False

                # Append number of G0s to the list once we determine start to end
                
                # If G0 is not the current instruction and counter is True (G0 commands counted), 
                # append the number of occurrences to the list
                if (self.gcode_flag is False) and (self.counter_flag is True):
                    self.repeating_list.append(self.count_occurrences)
                    self.count_occurrences = 0

                # Computes (calculates) the heights - stored as one list
                # Note: 6 is not a constant value based on the z starting position
                m_matrix = [self.pos[2] - (ix * 0.05) for ix in self.repeating_list] #compute the heights

                # Splits the array into "n" number of lists, where x is the total number of elements in each row of the grid
                r_matrix = [m_matrix[jx:jx + self.sampling_spot_y] for jx in range(0, len(m_matrix), self.sampling_spot_y)]


                
                ########################################
                #put heights into a grid
                ########################################
                
                
                # Keeps track of the row positions
                row_count = 0

                # Store heights in an array/list
                heights = []

                # Stores the heights in correct order to a list of lists
                for vector_position in r_matrix:
                    # If the row number is even, do not flip the list/array
                    if (row_count % 2 == 0):
                        heights.append(vector_position)
                    # If the row number is odd, flip the list/array
                    else:
                        reversed_heights = list(reversed(vector_position))
                        heights.append(reversed_heights)
                    row_count += 1

                ########################################
                # OPTION #1 - Excel Spreadsheet (File) #
                ########################################

                # Creates a Pandas DataFrame of the heights
                df = pd.DataFrame(heights)

                # Creates the excel workbook
                workbook = pd.ExcelWriter('Z_Heights.xlsx', engine='xlsxwriter')

                # Creates the excel worksheet and writes the heights to an excel spreadsheet
                df.to_excel(workbook, sheet_name='Sheet #1')

                # Closes the excel workbook
                workbook.close()

                #########################
                # OPTION #2 - Text File #
                #########################

                # Opens a new text file and writes the values for the z-heights to the file
                with open('heights_with_brackets.txt', 'w') as f:
                    for z_heights in heights:
                        f.write(str(z_heights).replace(',', '') + '\n')

                # Reading the Z_Heights text file line by line
                with open('heights_with_brackets.txt', 'r') as f:
                    # store in text variable
                    text = f.read()

                    # Getting the pattern for [],(),{} brackets and replace them to empty string
                    # creating the regex pattern & use re.sub()
                    pattern = re.sub(r"[\([{})\]]", "", text)

                # Appending the changes (z-heights without brackets) in new file
                # It will create new file in the directory and write the changes in the file.
                with open('Z_Heights.txt', 'w') as my_file:
                    my_file.write(pattern)
            self.counter = 0
            self.stop_sampling_flag = False
            time.sleep(1)
            self.cmd("M105")
            time.sleep(1)
            self.cmd("M114")
            

        #and wait for conductance value


        if self.gcodefile and self.gcodeidx < len(self.gcodelist) and self.response:#took out check for not moving

            self.response = False
            print('gcodeidx', self.gcodeidx)
            print('length of gcode list', len(self.gcodelist))
            self.sampling = True
            # if self.gcodeidx == 0:
            #     time.sleep(2)
            print(self.gcodeidx)#print the gcode index


            # Appends G-Code Instructions to a list
            self.gcode_instructions.append(self.gcodelist[self.gcodeidx])
            print('sending gcode')
            print('gcode:', self.gcodelist[self.gcodeidx])
            
            cmd = self.gcodelist[self.gcodeidx].split()
            if cmd[0].find("G1") != -1 and cmd[1].find("Z") != -1:
                self.current_position = round(float(cmd[1][1:]),2)

            elif cmd[0].find("G0") != -1 and cmd[1].find('Z-') != -1:
                self.current_position = self.current_position - float(cmd[1][2:])
                self.current_position = round(self.current_position,2)
             
            
            self.cmd(self.gcodelist[self.gcodeidx]) #will this work
            self.cmd("M400")
            self.cmd("M114")
            if cmd[0].find("G4") != -1:
                time.sleep(int(float(cmd[1][1:]))/1000)
            
            self.counter = self.counter + 1
            print('counter', self.counter)
            

            


            
            
            
            self.moving = True
          
            print('conductance', self.cond)
            
            """
            now I need to ask the printer for the conductance value every time it moves
            """
            if self.gcodelist[self.gcodeidx].find('G0 Z-') != -1 and self.cond <= self.con_threshold and self.cond >= self.lower_threshold:#G0 z- is for rapid negative z moevement
                self.gcodeidx = self.gcodeidx - 1 #send the same command again
                self.batch = True

            

            self.gcodeidx = self.gcodeidx + 1 #increment the gcode index process the next command
        while not self.got_conductance:
            self.get_conductance.emit(True)
                    #this will update the self.got_conductance flag
                    #this will get conductance value before every move
                    
        self.got_conductance = False
 
    def update_threshold(self, threshold, lower_threshold):##TODO: Unused
        self.con_threshold = threshold
        self.lower_threshold = lower_threshold
        
        print("Lower threshold updated to: %s" % (self.lower_threshold))
        print("threshold updated to: %s" % (self.con_threshold))
        
    def gcode_texts(self):
        pass

    def home(self):
        """
        home the printer
        """
        
        ##TODO: go to max z before homing that way it is level
        
        print("connect pinda probe!")
        #self.cmd("G0 Z210 F250") for now
        # TODO: open messagebox to confirm probe is connected
        self.cmd("M203 X5000 Y5000 Z5000") #set max shouldnt be here
        self.cmd("G28")
        
        #self.setposzero() removed for now
        
        self.cmd("M114")
        
        print("homing")
        self.homed = True
        
        
        
        
        
        
        
        
        

    def setposzero(self):
        """
        sets the current position to zero
        """
        self.cmd("G92 X0 Y0 Z0")

    def setposhundred(self): #BAD COMMAND TO USE
        #GOING TO TRY TO ERRADICATE ITS USE
        #sets the current position to 100, 100, 100
        self.cmd("G92 X100 Y100 Z100")

    def stop(self):
        
        """
        stop the console thread
        """
        self.prtconnect = False
        self.homed = False
        self.console.kill()
        self.console.terminate()
        self.terminate()

    def cmd(self, cmd_string):
        """send a command to the console

        Args:
            cmd_string (command): this is the command

        """
     

        #print(f"Sending command to printer: {cmd_string}")
        #print('sending command', cmd_string)

        if isinstance(cmd_string, str):

            self.console.stdin.write(cmd_string + '\n')  # write the command to the console

            self.console.stdin.flush() #flush the buffer (ensure the command is sent to subprocess)

        elif isinstance(cmd_string, list):
            for cmd in cmd_string:
                self.console.stdin.write(cmd + '\n')  # write the command to the console
                time.sleep(1)
                self.console.stdin.flush() #flush the buffer (ensure the command is sent to subprocess)
        else:
            print('cmd_string is not a string or list')
        
        
    def stop_sample(self): ##TODO: need to turn off flag eventually to run another one
        ##TODO: need to find a way to cancel the sampling process... maybe empty the list of gcode instructions
        """
        stop sampling process
        """
        
        #TODO:
        
        if self.conductance_mode:
            self.cmd("G90")
            self.cmd("G0 Z100 F3000")
            self.cmd("G0 X10 Y10 Z100 F3000")
            self.cmd("G91")
        else:
            self.cmd("G0 Z100 F3000")
            self.cmd("G0 X10 Y10 Z100 F3000")
        
        self.stop_sampling_flag = True
        self.gcodeidx = len(self.gcodelist) 
        print('Sampling stopped')
        
    def pause_sample(self):
        """
        pause the sampling process
        """
        self.last_pos = self.pos
        if self.conductance_mode:
            self.cmd("G90")
            self.cmd("G0 Z100 F3000")
            self.cmd("G0 X10 Y10 Z100 F3000")
            self.cmd("G91")
        else:
            self.cmd("G0 Z100 F3000")
            self.cmd("G0 X10 Y10 Z100 F3000")
        self.pause_sampling_flag = True
        
    def resume_sample(self):
        """resume the sampli  ng process
        """
        print("resuming")
        print("sending to", self.last_pos)
        if self.conductance_mode:
            self.cmd("G90")
            self.cmd("G0 X"+str(self.last_pos[0])+" Y"+str(self.last_pos[1])+ " Z"+str(self.last_pos[2])+" F2000")
            self.cmd("G91")
        # else:
        #     self.cmd("G0 X"+str(self.last_pos[0])+" Y"+str(self.last_pos[1])+ " Z"+str(self.last_pos[2])+" F2000")
        self.pause_sampling_flag = False
        
    def activate_loop(self):
        pass
       
    
        
    
if __name__ == '__main__':
    pass