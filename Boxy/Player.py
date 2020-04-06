import numpy as np  # pygame, copy,
#from random import randint
from Super_Classes import Body, Shape
import Box
import math
from Constants import G

##### Useful Identities ################################################################

dim = 2
max_fall_speed = 14.0
jump_strength = 14.0
crouch_bonus = 0.2 
#z_proj = [0.2,0.1,-1] # shift of 1 in z corresponds to this much shift in projected view

player_size = np.array([20,40])

##### Useful Functions  ################################################################


##### Classes           ################################################################

class Player(Body):
# Class for main character   
    def __init__(self,position):
        super().__init__(position,player_size-1,corporeal=True,solid=True,velocity=[0,0])  
        self.crouching = False
        self.sliding = False
        self.attacking = False
        self.shapes.append(Shape(self.self_shape(),(255,0,255),line_color = None,line_width = None)) # add visible shape for box
        self.size+= 1.0
    
    def gravity(self):
        # accelerate due to gravity
        #print(self.vel)
       # if isinstance(self.resting_on,Body):
       #     self.vel[1] = 0
       # else:
        self.vel[1] = min(max_fall_speed,self.vel[1]+G)
       # print(min(max_fall_speed,self.vel[1]+G))
       # print("#",self.vel)
        
    def jump(self):
        # flies upward, faster if crouching, not if airborne
        if isinstance(self.resting_on,Body):
            self.vel[1] = (-jump_strength*(1+ crouch_bonus*(self.crouching>0)))
            self.vel[0] += self.resting_on.vel[0] # add velocity of object being stood on
            self.is_off() # no longer standing on an object
    
    def crouch(self,keyval): # makes self smaller to crouch, bigger to uncrouch
        
        if self.crouching:
            if not keyval or not isinstance(self.resting_on,Body): # if key released or in the air, uncrouch
                self.pos[1] -= np.matmul(self.transform,self.size)[1]
                self.transform[0][:] *= 0.8
                self.transform[1][:] *= 2.0

                self.crouching = False
        else: # if uncrouched
            if keyval and isinstance(self.resting_on,Body): # down key pressed and on the ground
                self.transform[0][:] *= 1.25
                self.transform[1][:] *= 0.5
                self.pos[1] += np.matmul(self.transform,self.size)[1]
                self.crouching = True
           
        
    def walk(self,keyval,keyval2): # keyval = (is right key down) - (is left key down) or (is down key down) - (is up key down)
        accel = 200
        decel = 200
        top_speed = 3
        airborne = not isinstance(self.resting_on,Body)
        
        
        if airborne:# less control in the air. duh.
            accel = 0.1
            decel = 0.1
           # top_speed = 5
            
        if self.crouching:# can't crawl as fast as you can run... duh.
            top_speed = 1
            
        v = self.vel[0]
       # v2 = self.vel[2]
        
        if keyval == 0 or keyval*v <0:
          #  if keyval*v < 0: # active deceleration
          #      decel *=1.5
            if airborne:
                if abs(v)>0: # prevent decel into turning around
                   # print(self.vel)
                    self.vel[0] = v-math.copysign(min(accel,abs(v)),v)
                   # print('after:',self.vel)
            else: # if on ground, stop immediately
                self.vel[0] = 0
        else:
            if airborne:
                self.vel[0] = v+keyval*accel
            else:
                self.vel[0] = min(max(-top_speed,v+keyval*accel),top_speed) # prevent exceeding top speed
    
       # print('walking',self.vel)

            #### FOR THIRD DIMENSION ####
      #  if keyval2 == 0 or keyval2*v2 <0:
          #  if keyval2*v2 < 0: # active deceleration
          #      decel *=1.5
       #     if airborne:
        #        if abs(v2)>0: # prevent decel into turning around
         #           self.vel[2] = v2-math.copysign(min(accel*self.S,abs(v2)),v2)
          #  else: # if on ground, stop immediately
           #     self.vel[2] = 0
       # else:
       #     self.vel[2] = min(max(-top_speed*self.S,v+keyval2*decel*self.S),top_speed*self.S) # prevent exceeding top speed

   
   
   