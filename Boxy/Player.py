import numpy as np  # pygame, copy,
#from random import randint
from Super_Classes import Body, Shape
import Box
import math
from Constants import G, box_size, S

##### Useful Identities ################################################################

dim = 2
max_fall_speed = 12.0*S
jump_strength = 15.0*S
crouch_bonus = 0.2 
crawling_speed = 1.5*S
running_speed = 4.5*S
accel,decel = 0.15*S,.15*S
slide_duration = 10
slide_speed = 7.5*S
character_color = (255,0,255)
sliding_color = (200,0,200)

#z_proj = [0.2,0.1,-1] # shift of 1 in z corresponds to this much shift in projected view

player_size = np.array([box_size*.75,box_size*1.25]) # box size already contains S

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
    
    
    def draw(self,canvas,zero = np.array([0,0])):
        
        if self.sliding>0:
            color = sliding_color
        else:
            color = character_color
        for s in self.shapes:
            s.color = color
        
        super().draw(canvas,zero)
        
    
    # gravity, running, sliding, attacking, belly-flopping, gravity, all in one go
    def evolve(self,run_key,crouch_key,jump_key):
        
        # add gravity's effects
        self.vel[1] = min(max_fall_speed,self.vel[1]+G)
        
        # flags to determine effects of keystrokes
        airborne = not isinstance(self.resting_on,Body)
        decelerating = (run_key == 0 or run_key*self.vel[0] <0)

        
        if not airborne and jump_key and self.attacking<=0: #jump if on the ground and not attacking
            self.vel[1] = (-jump_strength*(1+ crouch_bonus*(self.crouching>0)))
            self.is_off() # no longer standing on an object
            self.sliding = 0 # cancels slides 
            airborne = True
            if abs(self.vel[0])>running_speed: # cannot maintain sliding speed in air
                self.vel[0] = math.copysign(running_speed,self.vel[0])
            
         
        if self.sliding>0: # sliding continues regardless of keys           
            self.sliding-=1  
            
        else: # if not sliding, some control  
            
            # deal with slide/crouch key
            if self.crouching:
                if not crouch_key or airborne: # if key released or in the air, uncrouch
                    self.pos[1] -= np.matmul(self.transform,self.size)[1]
                   # self.transform[0][:] *= 0.8
                    self.transform[1][:] *= 2.0
                    self.crouching = False
            else: # if uncrouched
                if not self.attacking and crouch_key and not airborne: # down key pressed and on the ground and not attacking

                    # crouch/slide position
                   # self.transform[0][:] *= 1.25
                    self.transform[1][:] *= 0.5
                    self.pos[1] += np.matmul(self.transform,self.size)[1]
                    self.crouching = True
                    
                    if run_key: # if already running, slide!
                        self.sliding = slide_duration # 10 frames of sliding!
                        self.vel[0] = slide_speed*run_key
            
        if self.sliding <=0:           
            if airborne or self.attacking>0: # if airborne or attacking, control is weak, cannot crouch or slide
                if decelerating:
                    self.vel[0] -= math.copysign(min(decel,abs(self.vel[0])),self.vel[0]) # decelerate but not past 0
                else: # accelerating
                    self.vel[0] += run_key*accel

            else: # else, on ground and not attacking, control is strong
                if decelerating:
                    self.vel[0] = 0 # stop immediately
                else: # accelerating
                    if self.crouching: # can't crawl as fast as you can run... duh.
                        top_speed = crawling_speed
                    else: # running
                        top_speed = running_speed

                    self.vel[0] =  top_speed*run_key # start walking/crawling at  speed
        
            

   