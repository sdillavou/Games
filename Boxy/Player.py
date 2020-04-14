import numpy as np  # pygame, copy,
#from random import randint
from Super_Classes import Body, Shape
import Box
import math
from Constants import G, box_size, S
from Make_Sounds import slide_sound

##### Useful Identities ################################################################

jump_strength = 8.0*G**2/S/0.8**2
crouch_bonus = 0.25
bounce_strength = jump_strength*(1.0+crouch_bonus)

slide_duration = 10
slide_speed = 7.5*S
sliding_color = (200,0,200)
slide_fraction = 1.1

max_fall_speed = jump_strength*(1.0+crouch_bonus) 
max_fly_speed = slide_speed
jump_key_relevance = 8 # for increasing jumps
jump_anticipation = 5 # for jump-bounces

crawling_speed = 1.5*S
running_speed = 4.5*S
accel,decel = 0.15*S,.3*S
walk_accel = running_speed/3.0
animate_length = 100

attack_duration = 10
attack_fraction = np.array([1.2,0.9],dtype='float')

crouch_fraction = 0.7
crouch_release_vel = -0.0001

flop_stun = 20
flop_bounce = -5.0*G**2/S/0.8**2
flop_width = 0.95

character_color = (30,30,30)


#z_proj = [0.2,0.1,-1] # shift of 1 in z corresponds to this much shift in projected view

player_size = np.array([box_size*.75,box_size*1.2]) # box size already contains S

##### Useful Functions  ################################################################


##### Classes           ################################################################

class Player(Body):
# Class for main character  

###############################################################################################
    def __init__(self,position):
        super().__init__(position,player_size/1.1,corporeal=True,solid=True,velocity=[0,0])  
        self.crouching = False
        self.sliding = 0
        self.attacking = 0
        self.flopping = 0
        self.jumping = 0
        self.shapes.append(Shape(self.self_shape(),(255,0,255),line_color = None,line_width = None)) # add visible shape for box
        self.size*= 1.1
        self.jump_anticipation = jump_anticipation
        self.animate = 0
        
        self.shift_path = [[player_size[0]*0.05*math.cos(2.0*i*math.pi/animate_length),player_size[0]*0.1*math.sin(4.0*i*math.pi/animate_length)] for i in range(animate_length)]
        
        # hitbox for attack
        self.attack_box = Body([0,0],player_size*attack_fraction,solid=False)
        self.attack_box.shapes.append(Shape(self.attack_box.self_shape(),color = (255,0,0),line_color = None)) # add outline
        # hitbox for slide
        self.slide_box = Body([0,0],player_size*np.array([slide_fraction,crouch_fraction*0.9],dtype='float'),solid=False)
        self.slide_box.shapes.append(Shape(self.slide_box.self_shape(),color = (255,0,0),line_color = None)) # add outline
        # hitbox for flop
        self.flop_box = Body([0,0],player_size*np.array([flop_width,crouch_fraction],dtype='float'),solid=False)
        self.flop_box.shapes.append(Shape(self.flop_box.self_shape(),color = (255,0,0),line_color = None)) # add outline
        

###############################################################################################
    # return relevant hit box (or None if no hit box being used)
    def hit_box(self):

        if self.sliding>0:
            self.slide_box.pos = self.pos*1.0
            return self.slide_box
        elif self.attacking>0:
            self.attack_box.pos = self.pos*1.0 + self.size*[0,1.0-attack_fraction[1]]
            return self.attack_box
        elif self.flopping==flop_stun:
            self.flop_box.pos = self.pos*1.0 + self.size*[0,1.0-attack_fraction[1]]
            return self.flop_box
        else:
            return None


###############################################################################################        
    
    def draw(self,canvas,zero = np.array([0,0])):

        if isinstance(self.hit_box(),Body): # draw relevant hit box
            self.hit_box().draw(canvas,zero)
        elif isinstance(self.resting_on,Body) and not self.crouching:
            super().draw(canvas,zero+self.shift_path[self.animate])
            self.animate += 1 + 3*(self.vel[0] !=0)
            self.animate %= len(self.shift_path)
            return
        
        super().draw(canvas,zero)

###############################################################################################
    # determine state of character
    # gravity, flopping, jumping, running, sliding, attacking, all in one go
    def evolve(self,run_key,crouch_key,jump_key,attack_key,flop_key,jump_hold):
       
    ######### FLAGS ###############################################

        is_airborne = not isinstance(self.resting_on,Body)
        is_decelerating = (run_key == 0 or run_key*self.vel[0] <0)
        is_attacking = self.attacking>0
        
        
    ######### GRAVITY #############################################
        
        if (self.jumping>0) and jump_hold: # if jump key is held after a jump, mantain velocity
            self.jumping -=1
        elif is_airborne: # otherwise let gravity do it's thing until the next jump
            self.vel[1] = min(max_fall_speed,self.vel[1]+G)
            self.jumping == 0
           
        
    ######### EVOLVE COUNTERS AND JUMP ############################
        
        if self.flopping>0:    # if flopping, that's all that's going on
            if not is_airborne:
                self.flopping -=1 # wait out stun
            return
                            
        #jump if on the ground and not attacking or flopping (already dealt with), character CAN jump out of slide
        if jump_key and not (is_airborne or is_attacking): # and not flopping 
            self.jump()
            return # this is the only action
           
        if self.sliding>0:     # only action during slides is jumping (already dealt with).          
            self.sliding-=1  
            return # this is the ony action
        
        if is_attacking:   # attacking doesn't stop movement control, so, onward!
            self.attacking -= 1  
        elif attack_key:
            self.attacking = attack_duration
        
        
    ######### CROUCH/FLOP ########################################

        # if not sliding or flopping or jumping, you can move!
        if self.crouching:
            if not crouch_key or is_airborne or is_attacking: # if key released or in the air, or attacking, uncrouch
                self.pos[1] -= np.matmul(self.transform,self.size)[1]*(1-crouch_fraction)
               # self.transform[0][:] *= 0.8
                self.transform[1][:] *= (1/crouch_fraction)
                self.crouching = False

                if not is_airborne: # if coming out of a crouch, give a small velocity to break boxes
                    if self.vel[1]>=0:
                        self.vel[1] = crouch_release_vel 

        else: # if uncrouched 
            if not is_attacking and crouch_key and not is_airborne: # crouch key pressed and on the ground and not attacking
                self.crouch(run_key) # crouch (or slide if running)
                if run_key != 0:
                    return # no walking/running if sliding

            if is_airborne and flop_key and not is_attacking: # if airborne, crouch pressed, and not attacking or flopping
                self.flop()
                return # no walking/running if flopping

            
    ######### MOVEMENT ###########################################
    
        if is_airborne: # if airborne control is weak
            if is_decelerating:
                self.vel[0] -= math.copysign(min(decel,abs(self.vel[0])),self.vel[0]) # decelerate but not past 0
            else: # accelerating
                self.vel[0] = max(-max_fly_speed,min(max_fly_speed,self.vel[0]+run_key*accel))

        else: # else, on ground, control is strong
            if is_decelerating:
                self.vel[0] = 0 # stop immediately
            else: # accelerating
                if self.crouching: # can't crawl as fast as you can run... duh.
                    top_speed = crawling_speed
                else: # running
                    top_speed = running_speed

                self.vel[0] = min(max(run_key*walk_accel+self.vel[0],-top_speed),top_speed) # accelerate not above top speed

    
####### functions used in evolve() written separately so that they can be externally utilized and code is easier to read      
    
    def crouch(self,run_key = 0):
        self.transform[1][:] *= crouch_fraction
        self.pos[1] += np.matmul(self.transform,self.size)[1]*(crouch_fraction) # bottom of body stays same
        self.crouching = True
        
        if run_key != 0: # if running, slide!
            self.sliding = slide_duration # 10 frames of sliding!
            slide_sound() # play that sound!
            self.vel[0] = slide_speed*run_key
    
    def flop(self):
        self.crouch()
        #self.transform[1][:] *= crouch_fraction
        #self.pos[1] -= np.matmul(self.transform,self.size)[1] # gain a little height (top of head stays the same)
        self.vel = np.array([0,flop_bounce],dtype='float') # stop moving horizontally, small bump vertically
        self.flopping = flop_stun
        
    def jump(self):
        self.vel[1] = (-jump_strength*(1+ crouch_bonus*(self.crouching>0)))
        self.is_off() # no longer standing on an object
        self.sliding = 0 # cancels slides 
        self.jumping = jump_key_relevance


####### external use, not used in evolve() #####

    def bounce(self,jump_timer,side):
        if self.vel[1] != crouch_release_vel: # if not just released from a crouch (this causes squeezing)
            if jump_timer>0 and side == -1:
                self.jumping = int(jump_key_relevance/2)
                self.vel[1] = side*bounce_strength 
                ## ADD CROUCH STRENGTH WHEN JUMPING ON SPRING BLOCK. DO JUST REGULAR JUMP WHEN BOUNCING ON SPRING BLOCK
            else:
                if side == 1:
                    self.vel[1] = min(bounce_strength,-self.vel[1]) # do not bounce down harder than collision was
                else: # side == -1
                    self.vel[1] = side*bounce_strength
                

            self.is_off() # no longer standing on an object
            self.sliding = 0 # cancels slides 
       