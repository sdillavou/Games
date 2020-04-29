import copy, numpy as np
from random import randint
from Super_Classes import Body, Shape
from Constants import box_size, G, protector_color, protector_line_color, protector_size, eye_color, rect
from Make_Sounds import wood_bounce_sound, wood_break_sound, boom_sound, countdown_sound
from Boomer import Boomer


##### Useful Identities ################################################################

#rot90mat = np.array([[0,-1],[1,0]],dtype='float')
identitymat = np.array([[1,0],[0,1]],dtype='float')


metal_color = (159,161,163)
wood_color = (200,100,0)
dark_wood_color = (180,80,0)
nitro_color = (10,170,10)
tnt_color = (200,0,0)
tnt_letter_color = (230,200,50)
tnt_light_color = (255,100,100)
nitro_letter_color = (230,255,230)



# For drawing
break_scale = 1.3

# for timing
tnt_timing_sequence = 130
countdown_timings = np.round(tnt_timing_sequence*np.array([(4-i)/4 for i in range(4)]))-1

##### Useful Functions  ################################################################


# outputs nodes for T, given a scale
def t_shape(s=1,shift=[0,0],transform = identitymat,color=(0,0,0),line_color=None):
    shp = [tuple((i+j) for i,j in zip(shift,node)) for node in [(-3*s/4, -3*s/4), (-3*s/4, -s/4), (-s/4, -s/4), (-s/4, 3*s/4), (s/4, 3*s/4), (s/4, -s/4), (3*s/4, -s/4),(3*s/4, -3*s/4)]]
    t_shp = Shape(shp,color = color,line_color = line_color,z = 1)
    t_shp.transform(transform)
    t_shp.shift(shift)
    return t_shp

# outputs nodes for N, given a scale
def n_shape(s=1,shift=[0,0],transform = identitymat,color=(0,0,0),line_color=None):
    shp = [tuple((i+j) for i,j in zip(shift,node)) for node in [(-3*s/4, 3*s/4), (-3*s/4, -3*s/4), (-s/4, -3*s/4), (s/4, -s/16), (s/4, -3*s/4), (3*s/4, -3*s/4), (3*s/4, 3*s/4),(s/4, 3*s/4),(-s/4, s/16),(-s/4,3*s/4)]]
    n_shp = Shape(shp,color = color,line_color = line_color,z = 1)
    n_shp.transform(transform)
    n_shp.shift(shift)
    return n_shp


                    
def resolve_fall(bod,bod2): #resolving fall for non-character objects
    if bod2.solid and bod2.pos[1]>bod.pos[1]: # bod 2 is below and solid
        dim,gap = bod.overlap_dim(bod2)
        if dim == 1 and gap>=0.1:# bod2 is overlapping vertically
            bod.is_on(bod2)
            bod.recursive_shift([0,-gap]) #shift bod (and those resting on it) up!
            return True # solved!
    return False


##### Classes           ################################################################


########################################################################################
########################################################################################
# Superclass for all box types, defines size

class Box(Body): 
    destruct_scale = break_scale
    size = [box_size,box_size]
    destruct_time = 10
    player = None # all boxes track the player to add to status/interact
   
    
    # Initialize box with location and color
    def __init__(self,position,color,line_color = (0,0,0),line_width = 2,floating=False):   
        Body.__init__(self,position,self.size,True,True,[0,0]) 
        self.shapes.append(Shape(self.self_shape(),color,line_color = line_color,line_width = line_width)) # add visible shape for box
        self.destruct_counter = -1 
        self.floating = floating
        self.fruit = 0
        self.lives = 0
        self.bounces = -1
        self.hit_box = None # no hit box unless boom_box and exploding
        
        
    # Boxes are subject to gravity if not designated as floating and not resting on an object and also are solid/corporeal
    def move(self):
        if not self.floating and not isinstance(self.resting_on,Body) and self.solid and self.corporeal:
            self.vel[1] += G
        Body.move(self)
        
    
    def draw(self,canvas,zero = np.array([0,0])):
        if self.destruct_counter == self.destruct_length: # remove box
            self.shapes[0].color = None
            self.shapes[0].line_color = None
        Body.draw(self,canvas,zero)
    
    def destroy(self, get_goodies=False):
        
        Body.destroy(self)       # make non-corporeal
        # add goodies to the status if DESERVED
        self.player.current_status.gobble_box(self,get_goodies)
       
   
        
########################################################################################
########################################################################################   
# Sub-classes to handle groups of boxes

# Class to handle destructable boxes than can bounce player 
class Bounce_Box(Box):
     
    
     def break_or_bounce(self,player):

        dim,side,converging = Body.interact(self,player) # solid interactions
        
        if dim == 1: # self and player collide vertically
            
            bounce = converging # must be converging to bounce
            if bounce and self.bounces>0:
                self.bounces -=1
            
            # box breaks if last allowable bounce or it is falling
            break_box = (bounce and (self.bounces == 0 or self.vel[1]>0)) 
            
            # edge cases where box must break when hit from below
            if bounce and side == 1:
                # player on a solid object and hitting underside 
                if isinstance(player.resting_on,Body):
                    break_box = True
                    bounce = False # no need to bounce
                    player.jumping = 0 # no longer jumping, buddy
                    
            return break_box, bounce*side # return side if bouncing
        
        else: # not colliding vertically, no break or bounce
            return False, False
    
########################################################################################

# Class to handle explosive boxes
class Boom_Box(Box,Boomer):
    
        
    # What happens when this explosive dies
    def destroy(self): 
        Box.destroy(self,False)      # make non-corporeal, no goodies (not that there are any)
        Boomer.explode(self) # sound and hit box

        
########################################################################################
########################################################################################
# Specific boxes

# Class for metal boxes
class Metal(Box):

    # Initialize metal box
    def __init__(self,position,floating=False):
        Box.__init__(self,position,metal_color,floating=floating)
        shp = Shape(self.self_shape(),color=None,line_color = (0,0,0),line_width = 2)
        shp.transform([[0.02,0],[0,0.02]])
        for i in [-self.size[0]*.7, self.size[0]*.7]:
            for j in [-self.size[0]*.7, self.size[0]*.7]:
                shp2 = copy.deepcopy(shp)
                shp2.shift([i,j])
                self.shapes.append(shp2) # add corner dots

    def destroy(self, get_goodies=False): # can't be destroyed, sucka
        pass
       
########################################################################################

# Class for wooden boxes
class Wood(Bounce_Box):
        
    # Initialize wood box
    def __init__(self,position,floating=False):
        Box.__init__(self,position,wood_color,floating=floating)
        shp = [(-self.size[0]*0.65,-self.size[0]*0.8),(self.size[0]*0.65,-self.size[0]*0.8),(0,-self.size[0]*0.15)]
        tri = Shape(shp,color = dark_wood_color,line_color = dark_wood_color,line_width = 2)
        for _ in range(4):
            tri.rot90()
            self.shapes.append(copy.deepcopy(tri))
            
        self.bounces = 1 # regular wooden boxes can take exactly one bounce
        self.fruit = 1

        
    def destroy(self,get_goodies=False):
        Box.destroy(self,get_goodies)
        wood_break_sound()
        
    def interact(self,player):
        
        # if box is attacked in any way it breaks and doesn't impede player
        if self.overlap(player.hit_box()):
            self.destroy(True) # get them goodies
            return
        
        break_box, bounce = self.break_or_bounce(player) # inherited from Bounce_Box
       
        if break_box:
            self.destroy(True) # and get them goodies
           
        if bounce!=0: 
            player.bounce(bounce) # bounce up or down
            if not break_box:
                if isinstance(self,Bouncey_Wood):
                    player.current_status.counters['fruit'] += 1
                    wood_bounce_sound()

########################################################################################
        
# Wooden box with metal lining
class Metal_Wood(Box):
    # Initialize wood box
    def __init__(self,position,floating=False):
        super().__init__(position,metal_color,floating=floating)
        shp = [(-self.size[0]*0.65,-self.size[0]*0.8),(self.size[0]*0.65,-self.size[0]*0.8),(0,-self.size[0]*0.15)]
        tri = Shape(shp,color = wood_color,line_color = dark_wood_color,line_width = 2)
        for _ in range(4):
            tri.rot90()
            self.shapes.append(copy.deepcopy(tri))
        self.fruit = 1
        
 
    # interactions are standard solid unmoving UNLESS player is flopping
    def interact(self,player):
        
        # box can be broken from flopping
        if player.flopping == player.flop_stun and self.overlap(player.hit_box()):
            self.destroy(True) # get them goodies
            return
        
        # otherwise, indestructable platform
        Body.interact(self,player)
            
    def destroy(self,get_goodies=False):
        if get_goodies: # false if exploded, which doesn't work here
            Box.destroy(self,get_goodies)
            wood_break_sound()
    

########################################################################################

# class for volatile nitro boxes
class Nitro(Boom_Box):
    # Initialize nitro box
    def __init__(self,position,floating=False):
        super().__init__(position,nitro_color,floating=floating)
        self.shapes.append(n_shape(self.size[0],[0,0],[[8/15,0],[0,10/15]],nitro_letter_color,None)) # add N to front of box
        self.temporary_shift = [0,0]
    # Draw nitro, but randomly make it jump for a frame
    def draw(self,canvas,zero=np.array([0,0])): 

        if self.cooldown == 0:
            jump = (randint(0,100) < 1)
        
            if jump:
                self.temporary_shift = np.array([randint(-50,50),randint(-50,-20)],dtype='float')/20
                self.visual_shift([self.temporary_shift[0],0])
                self.visual_recursive_shift([0,self.temporary_shift[1]])
                self.cooldown = -1

        elif self.cooldown <=-1 :
            self.cooldown = 30
            self.visual_shift([-self.temporary_shift[0],0])
            self.visual_recursive_shift([0,-self.temporary_shift[1]])
            self.temporary_shift = [0,0]
        
        Boom_Box.draw(self,canvas,zero)
    
    
    # interactions are always death with nitro, baby.
    def interact(self,player):   
        # touching? blow up.
        if self.overlap(player) or self.overlap(player.hit_box()):
            self.destroy() # player death included in this line
            
########################################################################################

# Class for tnt boxes
class Tnt(Bounce_Box,Boom_Box):

    countdown_length = tnt_timing_sequence
    countdown_sounds = countdown_timings
    
    # Initialize tnt box
    def __init__(self,position,floating=False):
        super().__init__(position,tnt_color,floating=floating)
        for k in [-1,1]:
            self.shapes.append(t_shape(self.size[0],[k*5*self.size[0]/12,0],[[1/3,0],[0,5/12]],tnt_letter_color,None)) # add T to front of box
        self.shapes.append(n_shape(self.size[0],[0,0],[[1/3,0],[0,5/12]],tnt_letter_color,None)) # add N to front of box
        self.shapes[-1],self.shapes[-2] = self.shapes[-2],self.shapes[-1] # swap T and N
        self.countdown = -1
        self.bounces = -1 # does not immediately break from bouncing
    
    # Move needs to evolve state (countdown) and explode if necessary
    def move(self):
        
        Box.move(self)
        
        if self.countdown !=-1:
            self.countdown -=1
            if self.countdown == 0:
                self.destroy()
        
        if self.countdown > 0:
            if self.countdown in self.countdown_sounds:
                countdown_sound()
    
    def start_countdown(self):
        self.countdown = self.countdown_length
        for s in self.shapes[1:]: # TNT disapears temporarily
            s.visible = False
    
    # Draw Tnt, but randomly make it brighter for a frame
    def draw(self,canvas,zero=np.array([0,0])):     
       
        light_up = self.countdown!=-1 or ((randint(0,120) < 1) and self.cooldown == 0) # light up randomly or if counting down
        if light_up:
            self.shapes[0].color = tnt_light_color
            
        if self.countdown!=-1:
            for k,idx in enumerate(self.countdown_sounds):
                if self.countdown == idx:
                    self.shapes[k].visible = True
            
        Boom_Box.draw(self,canvas,zero) # boom box drawing
        
        if light_up and self.countdown == -1: # return color only if randomly lit
            self.shapes[0].color = tnt_color
            self.cooldown = 60
     
    # it's a boom box, baby
    def destroy(self):
        Boom_Box.destroy(self)
        self.countdown = -1 # no more sounds
      
    # tricky interactions with this here tnt box, it's got a detonate sequence, ya see   
    def interact(self,player):
     
        
        # if tnt box is attacked in any way it breaks and hits player
        if self.overlap(player.hit_box()):
            self.destroy()
            return
        
        break_box, bounce = self.break_or_bounce(player) # inherited from Bounce_Box
       
        if break_box:
            self.destroy()
            return

        if bounce!=0 and self.countdown == -1: # can only bounce if countdown isn't started
            player.bounce(bounce)                  # bounce up or down
            self.start_countdown()                 # start countdown!
                
                
########################################################################################             
                    
# Class for wooden boxes that can be bounced on multiple times
class Bouncey_Wood(Wood):
    # Initialize bouncy wood box
    def __init__(self,position,floating=False):
        super().__init__(position,floating)   
        self.shapes = self.shapes[0:1]
        for k in range(-2,3):
            self.shapes.append(Shape(rect([self.size[0]*0.08,self.size[1]*0.8],[self.size[0]*k/3,0]),color = dark_wood_color,line_color = dark_wood_color,line_width = 2))
            
        self.bounces = 10 # regular wooden boxes can take exactly one bounce, these do 10
        self.fruit = 1

########################################################################################
           
# Class for wooden boxes that contain protection sprites
class Protection(Wood):
    # Initialize protection wood box
    def __init__(self,position,floating=False):
        super().__init__(position,floating=floating)   
        self.shapes.append(Shape(self.self_shape(protector_size/box_size),protector_line_color,None,line_width = 2)) 
        self.shapes.append(Shape(self.self_shape(0.9*protector_size/box_size),protector_color,None,line_width = 2)) 
        self.shapes.append(Shape(self.self_shape([0.1,0.1]*protector_size/box_size),eye_color,None,line_width = 2))
        self.shapes[-1].shift(self.size*[0.3,-0.3]*protector_size/box_size) # eye facing one way
        self.shapes.append(Shape(self.self_shape([0.1,0.1]*protector_size/box_size),eye_color,None,line_width = 2)) 
        self.shapes[-1].shift(self.size*[-0.3,-0.3]*protector_size/box_size) # eye facing the other way
        self.fruit = 0 # no fruit inside   
            
    # if goodies, give that sprite!
    def destroy(self,get_goodies=False):
        if get_goodies:
            self.player.get_protection()# add protection from breaking this box 
        Wood.destroy(self,get_goodies) # get fruit (0) and box
        
#### Builder function ########################################################################

box_dict = {'metal':Metal, 'wood':Wood, 'metal_wood':Metal_Wood, 'tnt':Tnt, 'nitro':Nitro, 'bouncey_wood':Bouncey_Wood, 'protection':Protection}

def create_box(box_type,position,floating = False):
    return box_dict[box_type](position,floating)