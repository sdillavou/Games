import copy, numpy as np
from math import copysign
from Super_Classes import Body, Shape, Looper
from Constants import box_size, spikey_box, animate_path, rect, S
from Boomer import Boomer
from Make_Sounds import fruit_sound


##### Useful Identities ################################################################

owl_speed = 4
owl_size = box_size*np.array([0.8,0.5])
owl_color = (180,160,130)


##### Useful Functions  ################################################################





    
##### Classes           ################################################################


########################################################################################
########################################################################################
# Superclass for all baddie types

class Baddie(Body):
    
    # Initialize baddie with position and size
    def __init__(self,position,size,floating=False):   
        Body.__init__(self,position,size,True,True,[0,0]) 
        self.destruct_counter = -1 
        self.hit_box = None # no hit box unless boom_box and exploding
        self.animate = 0
        self.floating = floating
        self.direction = 1
        self.switchers = []
        self.animators = []
        self.shift_path = [np.array([0,0])]
        self.destroy_sound = fruit_sound
        
        
    # Baddies are subject to gravity if not designated as floating and not resting on an object and also are solid/corporeal
    def move(self):
        
        if not self.floating and not isinstance(self.resting_on,Body) and self.solid and self.corporeal:
            self.vel[1] += G
        
        if isinstance(self,Looper):
            Looper.move(self)
        else:
            Body.move(self)
        
        if self.vel[0] !=0:
            self.direction = copysign(1.0,self.vel[0])
            
        
        
    
    def draw(self,canvas,zero = np.array([0,0])):
        
        
        self.animate += 1 + 3*(any(self.vel !=0))
        self.animate %= len(self.shift_path)
            
        for s in self.switchers: # switch eyes, wings, feet, etc depending on direction
            s[0].visible = self.direction == -1
            s[1].visible = self.direction == 1
            
        for a in self.animators:
            a.shift(self.shift_path[self.animate])
               
        Body.draw(self,canvas,zero)
        
        for a in self.animators:
            a.shift(-self.shift_path[self.animate])
            
    
    # touching a baddie is bad. gotta hit with a kill box.
    def interact(self,player):
        
        # player hitting baddie kills it and vice versa
        if self.overlap(player.hit_box()): # player gets kill priority
            self.destroy() 
        
        elif player.overlap(self.hit_box):
            player.get_hit()
            
        elif self.overlap(player): 
            self.hit_player(player) # this can kill baddie too
            

    # how baddies should deal with hitting player      
    def hit_player(self,player):   
        player.get_hit()
        if player.protection>=0: # player didn't die, baddie should die
            self.destroy()

    def destroy(self):
        super().destroy()
        self.destroy_sound()
        
########################################################################################
########################################################################################   
# Sub-classes to handle groups of baddies

# Class to handle fliers that loop around
class Flier(Baddie,Looper):
    
     def __init__(self,path_pts,speed,size):
            
            Baddie.__init__(self,[0,0],[0,0],floating=True) # [0,0] location and size inputs for now
            
            # this needs to be modified to allow slowing down etc
            path = []
            for k in range(len(path_pts)-1):
                num_pts = abs(int(np.linalg.norm(np.subtract(path_pts[k],path_pts[k+1]))/speed))
                
                dummy = [np.linspace(path_pts[k][idx], path_pts[k+1][idx], num=num_pts,  dtype=float) for idx in range(2)]
                
                for i,j in zip(*dummy): #unpack dummy and put points into path
                    path.append([i,j])
            
            # reverse path and add it to complete the loop
            path = path + path[::-1]
            
            Looper.__init__(self,size,path,corporeal=True,solid=True)
            
        
########################################################################################

# Class to handle explosive baddies
class Boom_Baddie(Baddie,Boomer):

    # What happens when this explosive dies
    def destroy(self): #second input not used, just to allow for polymorphism
        Baddie.destroy(self)     
        Boomer.explode(self) 

        
########################################################################################
########################################################################################
# Specific boxes

# Class for metal boxes
class Owl(Flier):

    
    # Initialize metal box
    def __init__(self,path_pts):
        Flier.__init__(self,path_pts,owl_speed,owl_size)

        self.shapes.append(Shape(self.self_shape(),color=owl_color,line_color = (0,0,0),line_width = 2))
        self.shapes.append(Shape(rect([S*2,S*2]),color=(0,0,0),line_color = (0,0,0),line_width = 2))
        self.shapes[-1].shift(self.size*[-0.7,-0.55])
        self.shapes.append(Shape(rect([S*2,S*2]),color=(0,0,0),line_color = (0,0,0),line_width = 2))
        self.shapes[-1].shift(self.size*[0.7,-0.55])

        
        self.shapes.append(Shape(spikey_box([2*box_size/3,box_size/5],[0,0,0,1]),color=owl_color,line_color = (0,0,0),line_width = 2))
        self.shapes[-1].shift(self.size*[0.7,-0.55])
        self.shapes.append(Shape(spikey_box([2*box_size/3,box_size/5],[0,1,0,0]),color=owl_color,line_color = (0,0,0),line_width = 2))
        self.shapes[-1].shift(self.size*[-0.7,-0.55])
        
        self.switchers = [self.shapes[1:3], self.shapes[3:5]]
        self.animators = self.shapes[3:5]
        
        self.shift_path = animate_path([0,S*3],[0,2],150)
        
        
    # touching a baddie is bad. gotta jump on it.
    def interact(self,player):
        
        if player.overlap(self.hit_box):
            player.get_hit()   # not using self.hit_player(player) because this should never kill baddie
        
        dim,gap = Body.overlap_dim(self,player)
        if dim == 1 and (self.pos[1]>player.pos[1]): # player on top
            self.destroy()
            player.bounce(-1)
        
        elif dim !=-1: #otherwise touching is a problem for the player
            self.hit_player(player) # invulnerability takes care of multiple hits from one interaction 


########################################################################################
