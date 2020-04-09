import pygame, copy, numpy as np
from random import randint
from Super_Classes import Body, Shape
from Constants import box_size, G

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


##### Classes           ################################################################


# Superclass for all box types, defines size
class Box(Body): 
    destruct_length = 5

    size = [box_size,box_size]
    destruct_time = 10
    
    # Initialize box with location and color
    def __init__(self,position,color,line_color = (0,0,0),line_width = 2):   
        super().__init__(position,self.size,True,True,[0,0]) 
        self.shapes.append(Shape(self.self_shape(),color,line_color = line_color,line_width = line_width)) # add visible shape for box
        self.destruct_counter = -1
        self.floating = False
        
    def move(self):
        if not self.floating and not isinstance(self.resting_on,Body) and self.solid and self.corporeal:
            self.vel[1] += G
        super().move()
            
       
        
# Class for metal boxes
class Metal(Box):
    destruct_time = -1 
    # Initialize metal box
    def __init__(self,position):
        super().__init__(position,metal_color)
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
        super().__init__(position,wood_color)
        shp = [(-self.size[0]*0.65,-self.size[0]*0.8),(self.size[0]*0.65,-self.size[0]*0.8),(0,-self.size[0]*0.15)]
        tri = Shape(shp,color = dark_wood_color,line_color = dark_wood_color,line_width = 2)
        for _ in range(4):
            tri.rot90()
            self.shapes.append(copy.deepcopy(tri))
            
        self.bounces = 1 # regular wooden boxes can take exactly one bounce
    

    def draw(self,canvas,zero = np.array([0,0])):
        if self.destruct_counter == self.destruct_length: # remove box
            self.shapes[0].color = None
            self.shapes[0].line_color = None
        super().draw(canvas,zero,scale=break_scale)

class Metal_Wood(Box):
    # Initialize wood box
    def __init__(self,position):
        super().__init__(position,metal_color)
        shp = [(-self.size[0]*0.65,-self.size[0]*0.8),(self.size[0]*0.65,-self.size[0]*0.8),(0,-self.size[0]*0.15)]
        tri = Shape(shp,color = wood_color,line_color = dark_wood_color,line_width = 2)
        for _ in range(4):
            tri.rot90()
            self.shapes.append(copy.deepcopy(tri))
    
    def draw(self,canvas,zero = np.array([0,0])):
        if self.destruct_counter == self.destruct_length: # remove box
            self.shapes[0].color = None
            self.shapes[0].line_color = None
        super().draw(canvas,zero,scale=break_scale)
            
    
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
            
            
# Class for wooden boxes
class Bouncey_Wood(Wood):
    # Initialize bouncy wood box
    def __init__(self,position):
        super().__init__(position)   
        self.shapes = self.shapes[0:1]
        for k in range(-2,3):
            self.shapes.append(Shape(rect([self.size[0]*0.08,self.size[1]*0.8],[self.size[0]*k/3,0]),color = dark_wood_color,line_color = dark_wood_color,line_width = 2))
            
        self.bounces = 10 # regular wooden boxes can take exactly one bounce, these do 10
    