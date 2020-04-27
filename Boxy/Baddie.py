import copy, numpy as np
from math import copysign
from Super_Classes import Body, Shape, Looper
from Constants import box_size
from Boomer import Boomer


##### Useful Identities ################################################################

owl_speed = 5
owl_size = box_size*np.array([0.8,0.5])
owl_color = (150,50,100)


##### Useful Functions  ################################################################


def rect(size,shift=[0,0]):
        return [(-size[0]+shift[0],-size[1]+shift[1]),(-size[0]+shift[0],size[1]+shift[1]),(size[0]+shift[0],size[1]+shift[1]),(size[0]+shift[0],-size[1]+shift[1])]


    
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
        if any(self.vel!=0):
            self.animate+=3
        else:
            self.animate+=1
            
        Body.draw(self,canvas,zero)
        
    
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
