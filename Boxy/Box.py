import copy, numpy as np
from random import randint
from Super_Classes import Body, Shape
from Constants import box_size, G, protector_color, protector_line_color, protector_size, eye_color
from Make_Sounds import wood_bounce_sound, wood_break_sound, boom_sound, protection_sound


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

explode_scale = 1.4
break_scale = 1.3


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

def rect(size,shift=[0,0]):
        return [(-size[0]+shift[0],-size[1]+shift[1]),(-size[0]+shift[0],size[1]+shift[1]),(size[0]+shift[0],size[1]+shift[1]),(size[0]+shift[0],-size[1]+shift[1])]


    
                    
def resolve_fall(bod,bod2): #resolving fall for non-character objects
    if bod2.solid and bod2.pos[1]>bod.pos[1]: # bod 2 is below and solid
        dim,gap = bod.overlap_dim(bod2)
        if dim == 1 and gap>=0.1:# bod2 is overlapping vertically
            bod.is_on(bod2)
            bod.pos[1] -= gap #shift bod up!
            return True # solved!
    return False



##### Classes           ################################################################


# Superclass for all box types, defines size
class Box(Body): 
    destruct_length = 5

    size = [box_size,box_size]
    destruct_time = 10
    
    # Initialize box with location and color
    def __init__(self,position,color,line_color = (0,0,0),line_width = 2):   
        Body.__init__(self,position,self.size,True,True,[0,0]) 
        self.shapes.append(Shape(self.self_shape(),color,line_color = line_color,line_width = line_width)) # add visible shape for box
        self.destruct_counter = -1
        self.floating = False
        self.fruit = 0
        
    # Boxes are subject to gravity if not designated as floating and not resting on an object and also are solid/corporeal
    def move(self):
        if not self.floating and not isinstance(self.resting_on,Body) and self.solid and self.corporeal:
            self.vel[1] += G
        Body.move(self)
         
    # box is destructable if it has a positive destruct length
    def is_destructable(self):
        return destruct_length>0
        
# Class for metal boxes
class Metal(Box):
    destruct_time = -1 
    # Initialize metal box
    def __init__(self,position):
        Box.__init__(self,position,metal_color)
        shp = Shape(self.self_shape(),color=None,line_color = (0,0,0),line_width = 2)
        shp.transform([[0.02,0],[0,0.02]])
        for i in [-self.size[0]*.7, self.size[0]*.7]:
            for j in [-self.size[0]*.7, self.size[0]*.7]:
                shp2 = copy.deepcopy(shp)
                shp2.shift([i,j])
                self.shapes.append(shp2) # add corner dots

# Class for wooden boxes
class Wood(Box):
        
    # Initialize wood box
    def __init__(self,position):
        Box.__init__(self,position,wood_color)
        shp = [(-self.size[0]*0.65,-self.size[0]*0.8),(self.size[0]*0.65,-self.size[0]*0.8),(0,-self.size[0]*0.15)]
        tri = Shape(shp,color = dark_wood_color,line_color = dark_wood_color,line_width = 2)
        for _ in range(4):
            tri.rot90()
            self.shapes.append(copy.deepcopy(tri))
            
        self.bounces = 1 # regular wooden boxes can take exactly one bounce
        self.fruit = 1

    def draw(self,canvas,zero = np.array([0,0])):
        if self.destruct_counter == self.destruct_length: # remove box
            self.shapes[0].color = None
            self.shapes[0].line_color = None
        Body.draw(self,canvas,zero,scale=break_scale)
        
    def destroy(self):
        Body.destroy(self)
        wood_break_sound()
        
    def interact(self,player):
        jump_timer = 0
        
        # if box is attacked in any way it breaks and doesn't impede player
        if self.overlap(player.hit_box()):
            self.destroy()
            player.current_status.counters['fruit'] += self.fruit
            player.current_status.counters['boxes'] += 1
            return
        
        dim,side,converging = Body.interact(self,player) # solid interactions
        
        if dim > -1: # self and player overlap
            
            # will player bounce
            bounce = (dim == 1) and converging
            if bounce:
                self.bounces -=1
            
            #will box break
            break_box = (bounce and (self.bounces == 0 or self.vel[1]>0)) # falling bouncy boxes break
            
            # edge cases where box must break when hit from below (dim == 1 already if bounce)
            if bounce and side == 1:
                # player on a solid object and hitting underside or pressed jump this round (effectively a squeeze)
                if isinstance(player.resting_on,Body) or ((player.jump_recency == player.jump_anticipation) and (player.jumping > 0)):
                    break_box = True
                    bounce = False # no need to bounce
     

            if break_box:
                wood_break_sound()
                self.destroy()
                player.current_status.counters['fruit'] += self.fruit
                player.current_status.counters['boxes'] += 1
                
            if bounce: 
                player.bounce(side) # bounce up or down
                if not break_box:
                    if isinstance(self,Bouncey_Wood):
                        player.current_status.counters['fruit'] += 1
                        wood_bounce_sound()

        

class Metal_Wood(Box):
    # Initialize wood box
    def __init__(self,position):
        super().__init__(position,metal_color)
        shp = [(-self.size[0]*0.65,-self.size[0]*0.8),(self.size[0]*0.65,-self.size[0]*0.8),(0,-self.size[0]*0.15)]
        tri = Shape(shp,color = wood_color,line_color = dark_wood_color,line_width = 2)
        for _ in range(4):
            tri.rot90()
            self.shapes.append(copy.deepcopy(tri))
        self.fruit = 1
        
    def draw(self,canvas,zero = np.array([0,0])):
        if self.destruct_counter == self.destruct_length: # remove box
            self.shapes[0].color = None
            self.shapes[0].line_color = None
        super().draw(canvas,zero,scale=break_scale)
    
    # interactions are standard solid unmoving UNLESS player is flopping
    def interact(self,player):
        if player.flopping == player.flop_stun and self.overlap(player.hit_box()):
            self.destroy()
            player.current_status.counters['fruit'] += self.fruit
            player.current_status.counters['boxes'] += 1

            return
        
        Body.interact(self,player)
            
    def destroy(self):
        Body.destroy(self)
        wood_break_sound()
    
    
# Class for nitro boxes
class Nitro(Box):
    # Initialize nitro box
    def __init__(self,position):
        super().__init__(position,nitro_color)
        self.shapes.append(n_shape(self.size[0],[0,0],[[8/15,0],[0,10/15]],nitro_letter_color,None)) # add N to front of box
        self.temporary_shift = [0,0]
    # Draw nitro, but randomly make it jump for a frame
    def draw(self,canvas,zero=np.array([0,0])): 
        
        if self.cooldown != 0:
            self.cooldown -=1
        
        if self.cooldown == 0:
            jump = (randint(0,100) < 1)
        
            if jump:
                self.temporary_shift = np.array([randint(-50,50),randint(-50,-20)],dtype='float')/20
                self.visual_shift([self.temporary_shift[0],0])
                self.visual_recursive_shift([0,self.temporary_shift[1]])
                self.cooldown -=1

        elif self.cooldown <=-1 :
            self.cooldown = 30
            self.visual_shift([-self.temporary_shift[0],0])
            self.visual_recursive_shift([0,-self.temporary_shift[1]])
            self.temporary_shift = [0,0]
        
        super().draw(canvas,zero,scale = explode_scale)
    
    def destroy(self):
        Body.destroy(self)
        boom_sound()
    
    # interactions are always death with nitro, baby.
    def interact(self,player):   
        if self.overlap(player) or self.overlap(player.hit_box()):
            player.get_hit()
            player.current_status.counters['boxes'] += 1
            self.destroy()
            
        
# Class for tnt boxes
class Tnt(Box):

    # Initialize tnt box
    def __init__(self,position):
        super().__init__(position,tnt_color)
        for k in [-1,1]:
            self.shapes.append(t_shape(self.size[0],[k*5*self.size[0]/12,0],[[1/3,0],[0,5/12]],tnt_letter_color,None)) # add T to front of box
        
        self.shapes.append(n_shape(self.size[0],[0,0],[[1/3,0],[0,5/12]],tnt_letter_color,None)) # add N to front of box
        
    # Draw Tnt, but randomly make it brighter for a frame
    def draw(self,canvas,zero=np.array([0,0])):  
        if self.cooldown > 0:
            self.cooldown -=1
            
        light_up = (randint(0,120) < 1) and self.cooldown == 0
        if light_up:
            self.shapes[0].color = tnt_light_color
        super().draw(canvas,zero,scale=explode_scale)
        if light_up:
            self.shapes[0].color = tnt_color
            self.cooldown = 60
     
    def destroy(self):
        Body.destroy(self)
        boom_sound()   
      
    # tricky interactions with this here tnt box
    def interact(self,player):
        raise Exception('havent done this yet, bucko')
            
# Class for wooden boxes
class Bouncey_Wood(Wood):
    # Initialize bouncy wood box
    def __init__(self,position):
        super().__init__(position)   
        self.shapes = self.shapes[0:1]
        for k in range(-2,3):
            self.shapes.append(Shape(rect([self.size[0]*0.08,self.size[1]*0.8],[self.size[0]*k/3,0]),color = dark_wood_color,line_color = dark_wood_color,line_width = 2))
            
        self.bounces = 10 # regular wooden boxes can take exactly one bounce, these do 10
        self.fruit = 1
        
           
# Class for wooden boxes
class Protection(Wood):
    # Initialize protection wood box
    def __init__(self,position):
        super().__init__(position)   
        self.shapes.append(Shape(self.self_shape(protector_size/box_size),protector_line_color,None,line_width = 2)) 
        self.shapes.append(Shape(self.self_shape(0.9*protector_size/box_size),protector_color,None,line_width = 2)) 
        self.shapes.append(Shape(self.self_shape([0.1,0.1]*protector_size/box_size),eye_color,None,line_width = 2))
        self.shapes[-1].shift(self.size*[0.3,-0.3]*protector_size/box_size) # eye facing one way
        self.shapes.append(Shape(self.self_shape([0.1,0.1]*protector_size/box_size),eye_color,None,line_width = 2)) 
        self.shapes[-1].shift(self.size*[-0.3,-0.3]*protector_size/box_size) # eye facing the other way
        self.fruit = 0 # no fruit inside
        
    def interact(self,player):
        Wood.interact(self,player)
        if not self.corporeal: # got destroyed by above interaction
            player.protection += 1 # add protection from breaking this box
            protection_sound()   
      