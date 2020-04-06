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
crawling_speed = 1.5
running_speed = 4.5
#z_proj = [0.2,0.1,-1] # shift of 1 in z corresponds to this much shift in projected view

player_size = np.array([20,40])

##### Useful Functions  ################################################################


##### Classes           ################################################################

class Player(Body):
# Class for main character   
    def __init__(self,position):
        super().__init__(position,player_size-1,corporeal=True,solid=True,velocity=[0,0])  
        self.crouching = False
        self.sliding = 0
        self.attacking = 0
        self.shapes.append(Shape(self.self_shape(),(255,0,255),line_color = None,line_width = None)) # add visible shape for box
        self.size+= 1.0
    
    
    
    
    def gravity(self):
        self.vel[1] = min(max_fall_speed,self.vel[1]+G)
 
    def jump(self):
        # flies upward, faster if crouching, not if airborne
        if isinstance(self.resting_on,Body):
            self.vel[1] = (-jump_strength*(1+ crouch_bonus*(self.crouching>0)))
           # self.vel[0] += self.resting_on.vel[0] # add velocity of object being stood on
            self.is_off() # no longer standing on an object
    
    # based on crouch key, adjust size and position to lower player to the ground.
    def crouch(self,crouch_keyval,run_keyval=0): 
        if self.sliding == 0: # if not sliding. this button doesn't do anything if sliding
            if self.crouching:
                if not crouch_keyval or not isinstance(self.resting_on,Body): # if key released or in the air, uncrouch
                    self.pos[1] -= np.matmul(self.transform,self.size)[1]
                    self.transform[0][:] *= 0.8
                    self.transform[1][:] *= 2.0
                    self.crouching = False
            else: # if uncrouched
                if crouch_keyval and isinstance(self.resting_on,Body): # down key pressed and on the ground
                    if run_keyval: # if already running
                        self.sliding = 10 # 10 frames of sliding!
                        
                    else: # if not running, just crouch
                        self.transform[0][:] *= 1.25
                        self.transform[1][:] *= 0.5
                        self.pos[1] += np.matmul(self.transform,self.size)[1]
                        self.crouching = True
           
      
    # based on walking (L/R) keys, modify velocity if standing on an object
    def walk(self,keyval,keyval2): # keyval = (is right key down) - (is left key down) or (is down key down) - (is up key down)
        airborne = not isinstance(self.resting_on,Body)
        decelerating = (keyval == 0 or keyval*self.vel[0] <0)

        if airborne:# less control in the air. duh.
            accel,decel = 0.1,0.1
        
            if decelerating:
                self.vel[0] -= math.copysign(min(decel,abs(self.vel[0])),self.vel[0]) # decelerate but not past 0
            else: # accelerating
                self.vel[0] += keyval*accel
            
        else: # if on the ground, stop and start immediately     
            if decelerating:
                self.vel[0] = 0 # stop immediately
            else: # accelerating
                if self.crouching: # can't crawl as fast as you can run... duh.
                    top_speed = crawling_speed
                else: # running
                    top_speed = running_speed

                self.vel[0] =  top_speed*keyval # start walking/crawling at  speed
            
       
   