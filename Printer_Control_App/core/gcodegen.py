'''
Control mechanism to check if conductance meter is connected when G30 (return to reference point
after sampling) is used probing is used
'''

import os
import numpy as np
import datetime as dt

# Import pandas
import pandas as pd

# Imports re-module for creating regex expression
import re

'''
class for X and Y coordinate that contains startpos, resolution and 
length.
This class is a sub class of Gcode class and is used in __init__ of 
Gcode. Based on input an array called path is generated that contains 
the X or Y of the sampling spots
'''
class Coor(object): #generates path of sampling spots in X and Y direction
        def __init__(self,start,res,length):
                if res==0: #sample same spot
                        self.path = []
                        for x in range (0,length):
                                self.path.append(start)
                else:
                        self.startum=int(start*1000) #start position in um
                        self.resum=int(res*1000) #resolution in um
                
                        self.lengthum=int(length*1000) #length in um
                        self.path = [] #array to store path of sampling spots
                        for x in range (0,int(self.lengthum/self.resum)): #loop to generate path
                                self.path.append(x*self.resum)
                        #adding start position to each item of array
                        self.path = [(x + self.startum)*0.001 for x in self.path]       

                #i dont get the math here what is it doing?
'''
each instance of class Gcode is a Gcode for a set of variables that 
are determined above.
class Coor is used to group variables belonging to X and Y
'''
class Gcode(object):


        def __init__(self):

                print("gcode init function")
                # list where final gcode is stored in
                self.codelist = []

                ####--------------------Spatial variables--------------------------####
                # position of first sampling spot
                self.startx = 0  # Start Position X
                self.starty = 0  # Start Position Y
                self.startz = 0  # Start Position Z

                # sampling resolution in each direction (mm)
                self.resx = 0  # Resolution X
                self.resy = 0  # Resolution Y

                # Number of sampling spots/patches in each direction
                self.setx = 0  # Number of Sampling Spots X
                self.sety = 0  # Number of Sampling Spots Y

                ####--------------------Times--------------------------####
                # sampling time in seconds (3-8 seconds)
                self.st = 0

                # pause after sampling (default 10 seconds) used for conductance to stabilize
                self.pause = 0

                ####--------------------Speeds--------------------------####
                # probe speed (downwards) in z
                self.z_speed = 0
                

                # lifting speed in Z (default 20mm/s)
                self.zspeedup = 0

                # xy travel speed in mm/min 5000: very fast 1000:fast, 500: slow
                self.speedxy = 0

                ####--------------------Filename for gcode file output--------------------------####
                self.filename = "filename" #change to date?

                ####--------------------Sampling Mode--------------------------####
                self.probe = False  # False:manually True: G30 conductance

                ####-------------------Conductance Probing (self.probe = True)----------------------####
                # z retraction (upwards) after sampling
                #self.retz = 0

                # Additional Sampling after tissue touched (downwards, if conductance meter is too sensitive)
                #self.zoff = 0
                self.step = 0.05

                ####------------------Constant Probing (self.probe = False) ------------------------####

                # lower z position that touches droplet ( must be smaller than z start)
                self.lz = 0
                
                self.zspeed = 0
               
                self.ref_probe = False
                
                self.ref_flag = False
                self.ref_end_flag = False
                
                self.ref_both_flag = False
                
                self.ref_x = 0
                self.ref_y = 0
                self.ref_z = 0
                self.ref_dwell = 0
                self.ref_sample = 0
                
                self.xy_acceleration = 1250 #mm/s^2
                self.z_acceleration = 400 #mm/s^2
                
                self.ref_z_first = False #if true goes to specified z beofre going to x and y

        def calc(self):
                ####------------------Calculated values based on input ------------------------####
                # length in each direction based on values above TODO: widget that shows lengths
                print("SetX ", self.setx)
                print("SetY ", self.sety)
                print("ResX ", self.resx)

                if self.resx == 0:#sample same spot
                        self.lengthx = self.setx
                else:
                        self.lengthx=self.setx*self.resx
                if self.resy == 0: #sample same spot
                        self.lengthy = self.sety
                else:
                        self.lengthy=self.sety*self.resy

                print("StartX ", self.startx)
                print("StartZ ", self.startz)
                starting_z_positions = self.startz
                print("ResX ", self.resx)
                print("LengthX ", self.lengthx)

                self.x=Coor(self.startx, self.resx, self.lengthx)
                self.y=Coor(self.starty, self.resy, self.lengthy)

                print("X Path ",self.x.path)
                #define two dimenstional array to store X/Y coord.
                #length l is product of path arrays of X and Y
                l=len(self.y.path)*len(self.x.path)
                self.pathtable = [[0 for x in range(2)] for y in range(l)]

                print("Path Table ",self.pathtable)

                # unit conversion for times
                self.stms=self.st*1000
                self.pausems=self.pause*1000
                
                #variable to estimate printing time just based on 
                #sampling time and pauses. Inaccurate especially
                #when G30 sampling is used.
                self.eta=0
                self.eta_list = []

                #variables to estimate distance moved
                self.dist=0                     
                self.x1=0
                self.y1=0
                self.z1=0



       
        
        def Zspeed(self,zspeed):      
                '''
                set the speed of the z axis
                
                zspeed (int): the speed of the z axis
                '''                                  
                #self.codelist.append(("\nM203 Z%f") %(zspeed)) #comment out for now
                self.z_speed=zspeed
        def refrence(self, x, y, dwell_time, sample_time, z = None): #TODO fix
                print(self.ref_z_first)
                '''
                #Sets the reference point for the printer head
                '''
                #precondition: if z is none probe for self_prober is true
                
                if self.probe and not self.ref_probe:
                        #need to set probe to false then true
                       
                        #code
                        if self.ref_z_first:
                                self.Zspeed(self.zspeed)
                                self.appendPosZ(z)
                                self.AppendPosXY(x,y)
                        else:
                                self.AppendPosXY(x,y) #set position for x and y
                                self.Zspeed(self.zspeed)
                                self.AppendPos(x,y,z)
                        self.AppendPause((int(sample_time)*1000))
                        self.Zspeed(self.zspeedup)
                        self.AppendPos(x,y,self.startz)
                        self.AppendPause(int(dwell_time)*1000)
                        
                        
                 
                    
                elif not self.probe and self.ref_probe:
                        self.probe = True
                        
                        self.AppendPosXY(x,y)
                        self.AppendProbe(x,y) # adds G0 z- step command then sets back to absolute
                        self.AppendPause(int(sample_time)*1000) #pause for sampling time
                        self.Zspeed(self.zspeedup) #set z speed to zspeedup
                        self.AppendPos(x, y, self.startz) #set position for next movement
                        self.AppendPause(int(dwell_time)*1000)#pause for pausems
                
                        
                        
                        self.probe = False
                elif self.probe and self.ref_probe:
                        
                        self.AppendPosXY(x,y)
                        self.AppendProbe(x,y) # adds G0 z- step command then sets back to absolute
                        self.AppendPause(int(sample_time)*1000) #pause for sampling time
                        self.Zspeed(self.zspeedup) #set z speed to zspeedup
                        self.AppendPos(x, y, self.startz) #set position for next movement
                        self.AppendPause(int(dwell_time)*1000) #pause for pausems
                else:
                        if self.ref_z_first:
                                self.Zspeed(self.zspeed)
                                self.appendPosZ(z)
                                self.AppendPosXY(x,y)
                        else:
                                self.AppendPosXY(x,y) #set position for x and y
                                self.Zspeed(self.zspeed)
                                self.AppendPos(x,y,z)
                        self.AppendPause(int(sample_time)*1000)
                        self.Zspeed(self.zspeedup)
                        self.AppendPos(x,y,self.startz)
                        self.AppendPause(int(dwell_time)*1000)
        def AppendPos(self,x,y,z, speed = None): #going to be obsoluete soon
                '''
                set the position of the printer head (added tp list of commands)
                x (int): x position
                y (int): y position
                z (int): z position
                '''
                if speed:
                        self.codelist.append(("\nG1 Z%f F%f") %(z, speed))
                else:
                        self.codelist.append(("\nG1 Z%f F%f") %(z, self.zspeedup)) #set z speed
                        self.codelist.append(("\nG1 X%f Y%f F%f") %(x,y,self.speedxy))
                self.dist=self.dist+abs(self.x1-x)+abs(self.y1-y)+abs(self.z1-z)
                distance = max(abs(self.x1-x), abs(self.y1-y))
                time = self.calculate_travel_time(distance, self.speedxy)
                time += self.calculate_travel_time(abs(self.z1-z), self.zspeedup)
                self.eta += time
                self.eta_list.append(time)
                self.x1=x
                self.y1=y
                self.z1=z
                
        def appendPosZ(self,z):
                self.codelist.append(("\nG1 Z%f F%f") %(z, self.z_speed))
                self.z1=z
                self.dist = abs(self.z1-z)
                distance = abs(self.z1-z)
                time = self.calculate_travel_time(distance, self.z_speed)
                self.eta += time
                self.eta_list.append(time)
                
        def AppendPosXY(self,x,y):
                '''
                set the position of the printer head ***ONLY X AND Y*** (added tp list of commands)
                x (int): x position
                y (int): y position
                '''
                self.codelist.append(("\nG1 X%f Y%f F%f") %(x,y,self.speedxy))                
                self.dist=self.dist+abs(self.x1-x)+abs(self.y1-y)
                distance = max(abs(self.x1-x), abs(self.y1-y))
                time = self.calculate_travel_time(distance, self.speedxy)
                self.eta += time
                self.eta_list.append(time)

                self.x1=x
                self.y1=y
                


        #Appends pause for sampling (st) and pause before sampling
        #(pause)
        def AppendPause(self,ms):
                '''
                PAUSE THE PRINTER HEAD for a certain amount of time
                
                ms (int): the amount of time to pause the printer head
                '''
                
                self.codelist.append(("\nG4 P%f") %(ms)) #pause and wait for ms milliseconds
                self.eta=self.eta+(ms/1000) #to seconds
                self.eta_list.append(ms/1000)

               
        def Sampling(self,x,y):
                '''
                #Performs sampling movement and moves back above patch 
                x (int): x position
                y (int): y position
        
                '''
                self.AppendPosXY(x,y) #set position for x and y
                #check for probing mechanism
                if (self.probe==True):   #conductive                                                                            #statement to determine probing
                        self.AppendProbe(x,y) # adds G0 z- step command then sets back to absolute
                        self.AppendPause(self.stms) #pause for sampling time
                        self.Zspeed(self.zspeedup) #set z speed to zspeedup
                        self.AppendPos(x, y, self.startz) #set position for next movement
                        self.AppendPause(self.pausems) #pause for pausems
                else: #manually
                        self.Zspeed(self.zspeed)
                        self.appendPosZ(self.lz)
                        self.AppendPause(self.stms)
                        self.Zspeed(self.zspeedup)
                        self.appendPosZ(self.startz)
                        self.AppendPause(self.pausems)
                

         
        def AppendProbe(self,x,y):
                '''
                #Probing movement adds G0 z- step command then sets back to absolute
                        
                x and y not needed
                '''                          
                self.Zspeed(self.zspeed)
                self.AppendRelative()
                print(self.zspeed)
                #self.codelist.append(("\nG0 Z-%f F%f" % (self.step, self.Zspeed))) #step down
                self.codelist.append("\nG0 Z-%f F%f" % (self.step, self.zspeed))
                self.AppendAbsolute()
                '''
                #self.codelist.append("\nG30")
                #self.codelist.append("\nG92 Z0")

                #self.AppendZoff()
                self.AppendPause(self.stms)


                self.Zspeed(self.zspeedup)
                self.AppendRelative()
                self.AppendPos(0,0,self.retz)
                self.AppendAbsolute()
                self.AppendPause(self.pausems)
                '''
        def AppendZoff(self):
                '''
                
                '''
                #self.AppendPause(2000)
                #self.AppendResetZ()
                self.AppendRelative()
                #self.AppendPos(0,0,((self.zoff)))
                self.AppendAbsolute()

        
        def AppendRelative(self):
                self.codelist.append("\nG91") #relative positioning (ie moves 10 units from where it is right now)

        def AppendAbsolute(self):
                self.codelist.append("\nG90") #absolute positioning (set direct coordinates)

        def AppendResetZ(self):
                self.codelist.append(("\nG92 Z1")) #reset Z axis to 1

        #Saves codelist array in an textfile in the folder that
        #contains this script
        def Save(self):
                '''
                save the gcode to a file
                '''
                folder = 'Gcode'
                
                #remove commas from gcode list
                
                self.codestr=' '.join(self.codelist)
                

                file_path = str(self.filename) + '.gcode'
                with open(file_path, "w") as output:
                        output.write(str(self.codestr))
                print(("Saved as: %s.gcode") %(self.filename))
                

        
                with open('eta.txt', 'w') as f:
                        for eta in self.eta_list:
                                f.write(f"{eta}\n")



       
        def Path(self):
                '''
                #attaches X/Y coordinates to two dimensional array
                #pathtable in loop functions.
                #Zig zag path is obtained through if statement
                '''
                ct=0
                for idy, i in enumerate(self.y.path):
                        for idx, k in enumerate(self.x.path):
                                if (idy%2) == 0:
                                        self.pathtable[ct][0]= self.x.path[idx]
                                        self.pathtable[ct][1]= self.y.path[idy]
                                else:
                                        self.pathtable[ct][0]=self.x.path[-(idx+1)]
                                        self.pathtable[ct][1]=self.y.path[idy]
                                ct=ct+1

        
        def Code(self):
                '''
                # Applies sampling movement form Sampling funcion to each item
                # (set of coordinates) of array pathtable.
                '''

                self.count = 0
                self.Path()
                self.Zspeed(self.zspeed)
                self.AppendPos(self.pathtable[0][0],self.pathtable[0][1],self.startz)
                self.AppendPause(1000)
              
                if self.ref_flag and (not self.ref_end_flag or self.ref_both_flag): #should work
                       
                        self.refrence(self.ref_x, self.ref_y, self.ref_dwell, self.ref_sample, self.ref_z)
                      
                for k in self.pathtable:
                        #Debug: print(k[0],k[1])
                        self.Sampling(k[0],k[1]) #sampling movement
                if self.ref_flag and (self.ref_end_flag or self.ref_both_flag):
                        self.refrence(self.ref_x, self.ref_y, self.ref_dwell, self.ref_sample, self.ref_z)

                self.codelist.append(("\nG92 Z%f")%(self.startz))
                self.eta_list.append(self.calculate_travel_time(abs(self.startz-self.z1), self.zspeedup))
                #self.AppendPause(1000)
                #self.AppendPause(1000)
                #remove commas from gcode list
                #self.codelist=' '.join(self.codelist)

        def calculate_travel_time(self, dist, speed):
                """
                Calculate the travel time between two points using acceleration.
                Converts speed from mm/min to mm/s for computation.
                """
                speed = speed / 60  # convert speed to mm/s

                # Calculate the time to accelerate and decelerate
                t_acc = speed / self.xy_acceleration
                t_dec = speed / self.xy_acceleration

                # Calculate the distance to accelerate and decelerate
                d_acc = 0.5 * self.xy_acceleration * t_acc**2
                d_dec = 0.5 * self.xy_acceleration * t_dec**2
                d_const = abs(dist) - d_acc - d_dec

                # If there's no room for constant speed travel, recalculate times
                if d_const < 0:
                        # Simplified handling: assuming symmetrical acceleration and deceleration
                        t_acc = t_dec = (dist / self.xy_acceleration)**0.5
                        t_const = 0  # No constant speed phase
                else:
                        # Calculate the time to travel at constant speed
                        t_const = d_const / speed

                t_total = t_acc + t_dec + t_const
                print('Total travel time:', t_total)
                return t_total

 
                
                
                
        def generate(self): #seems to only be used in testing --Uneccessary--?
                '''
                generates gcode file based on input variables
                '''
                #Functions to generate Gcode
                self.calc() #generate path table
                self.Code() #generate path table
                self.Save() #save gcode filex
                print(f"ETA (Min:Sec): {int(self.eta // 60)}:{int(self.eta % 60):02d}")
                print(("Distance: %s mm")%(self.dist))
                print("Length of Code List ", len(self.codelist))
                print("path table: ",self.pathtable)


if __name__ == '__main__':
        File1=Gcode()
        File1.calculate_travel_time(180, 10000)
        