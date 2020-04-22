import numpy as np  # pygame, copy,
#from random import randint
from Super_Classes import Body, Shape, Vector
import math
import copy # remove this when you get a chance, it's inefficient
from Constants import G, box_size, S, character_color, protector_color, protector_line_color, protector_size, eye_color

from Make_Sounds import slide_sound, thud_sound, ouch_sound, power_down_sound


##### Useful Identities ################################################################

jump_strength = 8.0*G**2/S/0.8**2
crouch_bonus = 0.25
bounce_strength = jump_strength*(1.0+crouch_bonus)

slide_duration = 10
slide_speed = 7.5*S
slide_fraction = 1.15

max_fall_speed = jump_strength*(1.0+crouch_bonus) 
max_fly_speed = slide_speed
jump_key_relevance = 8 # for increasing jumps after the fact
bounce_jump_key_relevance = jump_key_relevance/2 # for bounces
jump_anticipation = 5 # how many frames prior can you press jump to increase a bounce

crawling_speed = 1.5*S
running_speed = 4.5*S
accel,decel = 0.15*S,.3*S
walk_accel = running_speed/3.0
animate_length = 100

attack_duration = 10
attack_fraction = np.array([1.2,1.1],dtype='float')


attack_color = (160,160,160)
spike_height = 5.0*S
approx_spike_size = 5.0*S

crouch_fraction = 0.7
crouch_release_vel = -0.0001

flop_stun = 20
flop_bounce = -5.0*G**2/S/0.8**2
flop_width = 0.95
flop_fraction = 0.15

invulnerable_timer = 45

legs_color = (200,50,50)
hand_color = legs_color
protector_color = (60,60,255)
protector_line_color = (255,255,255)

player_size = np.array([box_size*.85,box_size*1.2],dtype='float') # box size already contains S

rot90mat = np.array([[0,-1],[1,0]],dtype=float)

##### Useful Functions  ################################################################


def spikey_box(size,spike_sides=[1,1,1,1]):
    
    helper = [np.array([-1.0,-1.0]),np.array([1.0,-1.0]),np.array([1.0,1.0]),np.array([-1.0,1.0]),np.array([-1.0,-1.0])]
    nodes = []
    spikey_size = size*1.0 # new variable to avoid changing input size
    for i in range(2):
        spikey_size[i] -= sum(spike_sides[3-i::-2])*spike_height
    
    for side in range(4):
        nodes.append(spikey_size*helper[side])
 
        if spike_sides[side]:
            spike_num = int(2.0*spikey_size[(side)%2]/approx_spike_size/2.0)*2 +1

            half_spike = (spikey_size[side%2]*2.0)/(float(spike_num)*2.0-2.0)
            direction = (helper[side+1]-helper[side])
            step = half_spike*direction # move across this side in this direction
            add_spike = spike_height*np.array([direction[1],-direction[0]]) # way spikes jut out
            for k in range(1,spike_num):
                nodes.append(spikey_size*helper[side]+step*k+(k%2)*add_spike)
        
    return [tuple(n) for n in nodes]
    

##### Classes           ################################################################

class Player(Body):
# Class for main character  

    flop_stun = flop_stun

###############################################################################################
    def __init__(self,position):
        super().__init__(position,player_size,corporeal=True,solid=True,velocity=[0,0])  
        self.crouching = False
        self.sliding = 0
        self.attacking = 0
        self.flopping = 0
        self.jumping = 0
        self.shape_dict={'body':Shape(self.self_shape([0.95,0.9]),character_color,line_color = None,line_width = None)}
        self.shape_dict['body'].shift([0,-self.size[1]*0.1])
        self.shape_dict['legs'] = Shape(self.self_shape([0.9,0.01]),legs_color,line_color = None,line_width = None)
        self.shape_dict['legs'].shift([0,self.size[1]*.99])
        self.shape_dict['legs'].nodes[-1] = (0,0)
        self.shape_dict['crouch_body'] = Shape(self.self_shape(),character_color,line_color = None,line_width = None)
        self.shape_dict['hand'] = Shape(spikey_box(self.size*[0.2,0.25],spike_sides=[0,0,1,0]),hand_color,line_color = None,line_width = None)
        self.shape_dict['hand'].shift([0,self.size[1]*0.3])
        self.shape_dict['eye'] = Shape(self.self_shape([0.1,0.1]),eye_color,line_color = None,line_width = None)
        self.shape_dict['eye'].shift([0,-self.size[1]*0.7])
        
        
        for i in self.shape_dict.values(): # create standard list for holding shapes so they can be accessed both ways
            self.shapes.append(i)
        
        self.jump_anticipation = jump_anticipation
        self.jump_recency = 0
        self.animate = 0
        
        self.shift_path = [np.array([player_size[0]*0.05*math.cos(2.0*i*math.pi/animate_length),player_size[0]*0.1*math.sin(4.0*i*math.pi/animate_length)], dtype ='float' )for i in range(animate_length)]
        
        # hitbox for attack
        self.attack_box = Body([0,0],player_size*attack_fraction,solid=False)
       # self.attack_box.shapes.append(Shape(self.attack_box.self_shape(),color = (255,0,0),line_color = None))
        self.attack_box.shapes.append(Shape(spikey_box(self.attack_box.size,[1,1,1,1]),color = attack_color,line_color = None))
      #  self.attack_box.shapes[-1].shift(self.attack_box.size*[0,-attack_fraction[1]+1.0])
        
        # hitbox for slide
        self.slide_box = Body([0,0],player_size*np.array([slide_fraction,crouch_fraction*0.9],dtype='float'),solid=False)
        self.slide_box.shapes.append(Shape(spikey_box(self.slide_box.size,[0,1,0,1]),color = attack_color,line_color = None)) # add outline
        # hitbox for flop
        self.flop_box = Body([0,0],player_size*np.array([flop_width,crouch_fraction],dtype='float'),solid=False)
        self.flop_box.shapes.append(Shape(spikey_box(self.flop_box.size,[0,0,1,0]),color = attack_color,line_color = None)) # add outline
        
        self.direction = 1.0
        self.invulnerable = 0
        self.protection = 0
        
        self.protector = Protector(self.pos - self.size*[self.direction,1.0])
        
###############################################################################################
    # define relevant hit box (or None if no hit box being used)
    def hit_box(self):
        if self.sliding>0:                              # shift depending on direction
            self.slide_box.pos = self.pos*1.0  + self.direction*self.size*[slide_fraction-1.0,0]
            return self.slide_box
        elif self.attacking>0:
            self.attack_box.pos = self.pos*1.0 + self.size*[0,1.0-attack_fraction[1]]
            return self.attack_box
        elif self.flopping==self.flop_stun:
            self.flop_box.pos = self.pos*1.0 + self.size*[0,flop_fraction]
            return self.flop_box
        else:
            return None

###############################################################################################
    # get hit by something (die if no protection)
    def get_hit(self):
        if not self.invulnerable:
            ouch_sound()
            self.protection -= 1
            if self.protection>=0: # if any hits left, become invulnerable temporarily
                self.invulnerable = invulnerable_timer
                power_down_sound()
        # if invulnerable, ignore this hit

############################################################################################### 
    # get hit by something (die if no protection)
    def move(self):
        Vector.move(self) # no need to move objects ON self, as there are none
        self.protector.move() # move the protector
        
############################################################################################### 


    
    def draw(self,canvas,zero = np.array([0,0])):
        self.animate += 1 + 3*(self.vel[0] !=0)
        self.animate %= len(self.shift_path)
        
        
        if not (self.invulnerable and (self.animate % 5) == 0): # don't draw player every 5 frames when invulnerable
        

            body_shift = self.pos-zero
            self.shape_dict['legs'].draw(canvas,self.pos-(zero),self.transform)
            hand_shift = 0.0
            eye_shift = self.direction*self.size*[0.5,0.0]
            hand_trans = copy.deepcopy(self.transform)


            if isinstance(self.hit_box(),Body): # draw relevant hit box
                self.hit_box().draw(canvas,zero)

            if self.crouching: # includes sliding and flopping
                self.shape_dict['crouch_body'].draw(canvas,self.pos-(zero),self.transform)

                if self.flopping>0:
                    for k in [-1.0, 1.0]:
                        self.shape_dict['hand'].draw(canvas,body_shift+[k*self.size[0]*0.8,0])
                        self.shape_dict['eye'].draw(canvas,body_shift+k*eye_shift+[0,self.size[0]*0.1],self.transform*[3.0,1.0])
                else:
                    self.shape_dict['hand'].draw(canvas,body_shift+hand_shift,np.matmul(self.transform,self.direction*rot90mat))
                    self.shape_dict['eye'].draw(canvas,body_shift+eye_shift,self.transform)

            else: # if not crouched

                if isinstance(self.resting_on,Body) and not self.attacking>0:
                    body_shift -= self.direction*self.shift_path[self.animate]
                    hand_shift = -self.direction*self.shift_path[self.animate]*[4.0,0.5]
                else:
                    hand_trans[1,1] *= -1
                self.shape_dict['body'].draw(canvas,body_shift,self.transform)
                self.shape_dict['hand'].draw(canvas,body_shift+hand_shift,hand_trans)
                self.shape_dict['eye'].draw(canvas,body_shift+eye_shift,self.transform)
        
        
        if self.protection>0: # if protector is active, modify its velocity 
            
            self.protector.shapes[0].visible = self.protection == 2 #outermost outline only if double protector    
            self.protector.draw(canvas,zero,self.direction)
        
###############################################################################################
    # determine state of character
    # gravity, flopping, jumping, running, sliding, attacking, all in one go
    def evolve(self,keyboard):
    
        run_key = keyboard.right_key - keyboard.left_key
        crouch_key = keyboard.crouch_key
        jump_key = keyboard.jump_key
        attack_key = keyboard.attack_key
        flop_key = keyboard.flop_key
        jump_hold = keyboard.jump_hold
    
    
    ######### DIRECTION ###########################################

        if self.vel[0] !=0:
            self.direction = math.copysign(1.0,self.vel[0])

    ######### INVULNERABILITY and PROTECTOR #######################

        if self.invulnerable:
            self.invulnerable -=1
            
        self.protector.vel = 0.7*self.protector.vel + 0.03*(self.pos + self.shift_path[self.animate]*[2,4] - self.size*[self.direction,1.0] - self.protector.pos)
            
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
        
        # if flopping, that's all that's going on
        if self.flopping>0:    
            if not is_airborne:
                self.flopping -=1 # stun time decreases
            return
                            
        #jump if on the ground and not attacking or flopping (already dealt with), character CAN jump out of slide
        if jump_key and not is_attacking:
            self.jump_recency = self.jump_anticipation # key press can determine bounce if mid-air
            if not is_airborne: # can't jump mid air though.
                self.jump()
                return # jumping is the only action
        
        elif self.jump_recency>0: # count down from last jump key press
            self.jump_recency -=1
            
        # only action during slides is jumping (already dealt with).     
        if self.sliding>0:              
            self.sliding-=1  
            return # this is the only action
        
        # attacking doesn't stop movement control, so, onward!
        if is_attacking:   
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
        self.flopping = self.flop_stun
        
            
    def jump(self):
        self.vel[1] = (-jump_strength*(1+ crouch_bonus*(self.crouching>0)))
        self.is_off() # no longer standing on an object
        self.sliding = 0 # cancels slides 
        self.jumping = jump_key_relevance
        


####### external use, not used in evolve() #####

    def bounce(self,side):
        if self.vel[1] != crouch_release_vel: # if not just released from a crouch (this causes squeezing)
            if self.jump_recency>0 and side == -1:
                self.jumping = bounce_jump_key_relevance
                self.vel[1] = side*bounce_strength 
                ## ADD STRENGTH WHEN JUMPING ON SPRING BLOCK. DO JUST REGULAR JUMP WHEN BOUNCING ON SPRING BLOCK
            else:
                if side == 1:
                    self.vel[1] = min(bounce_strength,-self.vel[1]) # do not bounce down harder than collision was
                else: # side == -1
                    self.vel[1] = side*bounce_strength
                

            self.is_off() # no longer standing on an object
            self.sliding = 0 # cancels slides 
        
        
##### PROTECTOR CLASS  #################################################################


class Protector(Body):
    
    def __init__(self,position):   
        Body.__init__(self,position,protector_size,False,False,[0,0]) 
        self.shapes.append(Shape(self.self_shape([1.1,1.1]),protector_color,None,line_width = 2,visible=False)) 
        self.shapes.append(Shape(self.self_shape(),protector_line_color,None,line_width = 2)) 
        self.shapes.append(Shape(self.self_shape([0.9,0.9]),protector_color,None,line_width = 2))
        
        self.shapes.append(Shape(self.self_shape([0.1,0.1]),eye_color,None,line_width = 2)) 
        self.shapes[-1].shift(self.size*[0.3,-0.3]) # eye facing one way
        self.shapes.append(Shape(self.self_shape([0.1,0.1]),eye_color,None,line_width = 2)) # add visible shape
        self.shapes[-1].shift(self.size*[-0.3,-0.3]) # eye facing the other way
    
    # slightly more efficient move method than Body.move(), as there is never anything resting on it.
    def move(self):
        Vector.move(self)
        
    def draw(self,canvas,zero,direction):
        self.shapes[-1].visible = direction == -1
        self.shapes[-2].visible = direction == 1
        Body.draw(self,canvas,zero)