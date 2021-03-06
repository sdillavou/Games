import pygame, numpy as np
from Constants import S
#import pygame.gfxdraw

#####  Useful Matrices  ################################################################

rot90mat = np.array([[0,-1],[1,0]],dtype=float)
identitymat = np.array([[1,0],[0,1]],dtype=float)

#####      Classes      ################################################################

# Superclass for any object with location and velocity. 
class Vector:
    
    # Create & initialize position (and vel)      
    def __init__(self,position=[0,0],velocity=[0,0]): 
        self.pos = np.array(position,dtype=float)
        self.vel = np.array(velocity,dtype=float)
      #  print(self.vel)
      #  print(type(self.vel[1]))
    
    # Move this object
    def move(self):
        self.pos += self.vel # add vel to pos
    
    # print info (for debugging)
    def info(self):
        print(vars(self))
        
########################################################################################

# Class of Vectors with 2D size, and transformation. Can be visible, corporeal, and solid, and contains shapes to draw
class Body(Vector): 
    destruct_length = 6
    destruct_scale = 0.8
    
    # Create & initialize any specified variables  
    def __init__(self,position,size,corporeal=True,solid=True,velocity=[0,0]):     
        super().__init__(position,velocity)
        self.corporeal = corporeal             # can this object interact with others
        self.solid = solid                     # this object cannot pass through others
        self.size = np.array(size,dtype=float)             # rectangular size of this object (width/2, height/2)
        
        self.transform = np.copy(identitymat)  # transformation matrix, can change orientation, flip, and scale.       
        self.shapes = []                       # dictonary of shapes to draw
        self.cooldown = 0                     # generic counter to remember past effects
        self.resting_on = None                 # (Single) body this body is is resting on (if any)
        self.on_me = []                        # List of bodies resting on this body (if any) 
        self.destruct_counter = -1
        
        def transform_inverse(self):
            return numpy.linalg.inv(self.transform) 
        
    # Modify self.transform to change size, orientation, reflection
 #   def rot90(self,times = 1): # rotates body 90 degrees counter clockwise
 #       self.transform = np.matmul(np.linalg.matrix_power(rot90mat,times),self.transform)
 #   def flipud(self): # flips body up and down (from its current state)
 #       self.transform[1,:] *= -1
 #   def fliplr(self): # flips body left and right (from its current state)
 #       self.transform[0,:] *= -1
    
    def scale(self,multiple): # scales body by multiple (or x and y if multiple is length 2)
        if isinstance(multiple,float) or isinstance(multiple,int):
            self.transform *= multiple
        elif len(multiple) == 2:
            for i in range(2):
                self.transform[i,:] *= multiple[i]
        else:
            raise NameError('multiple is incorrect length')
            
 #   def return_to_size(self): # returns to original scale
 #       self.transform /= np.linalg.det(self.transform)
 #   def return_to_upright(self): # returns to original orientation
 #       self.transform = identitymat*np.linalg.det(self.transform)
        
    # do two bodies overlap
    def overlap(self,other): # could remove transform ability to speed computation?
        if other == None:
            return False
        else:
            overlaps =  (np.matmul(self.transform,self.size) + np.matmul(other.transform,other.size))-abs(self.pos-other.pos)
             # if all dimensions overlap (account for float error)
            return all(overlaps>-0.001) and any(overlaps>S) # and at least one is substantial (bigger than scale size)
       
    # returns dimension and overlap size of shallowest overlap (-1,None if no overlap)
    def overlap_dim(self,other): # could remove transform ability to speed computation?
        
        overlap_sizes = (np.matmul(self.transform,self.size) + np.matmul(other.transform,other.size)) - abs(self.pos-other.pos)
        
        # if all dimensions overlap (account for float error)
        if all(overlap_sizes>-0.0001) and any(overlap_sizes>S): # and at least one is substantial (bigger than scale size)
           # print(np.matmul(self.transform,self.size), np.matmul(other.transform,other.size),self.pos, other.pos)

           # print(overlap_sizes)
            return np.argmin(overlap_sizes) , np.min(overlap_sizes)
        else:
            return -1,overlap_sizes
        
        
    # sort the shapes by their z stack
    def sort_shapes(self):
        self.shapes = sorted(self.shapes, key= lambda x: x.z, reverse=False)
        
    # Draw Body's shapes, subject to position of the body
    def draw(self,canvas,zero=np.array([0,0])):  
        
        self.death_throws()
        
        if self.destruct_counter !=0:     
            for s in self.shapes:
                s.draw(canvas,self.pos-zero,self.transform)
        # if destruct counter = 0, no go
   
    # Move destruct counter down if needed.
    def death_throws(self):
         if self.destruct_counter > 0:
            self.destruct_counter -=1
            self.transform *= self.destruct_scale

    # Move and rotate this object
    def move(self):
        self.recursive_shift(self.vel)   
        if self.cooldown > 0:
            self.cooldown -=1  
    
    # recursively shift all objects that are resting on this one
    def recursive_shift(self,vel):
        # for all unique objects (no double counting) resting on this one
        for obj in set(self.recursive_obj_list()):
            obj.pos += vel
        
            
    def recursive_obj_list(self):
        out = [self]
        for obj in self.on_me:
            out += obj.recursive_obj_list()
        return out
       
    # shifts all SHAPES that are in this object
    def visual_shift(self,vel):
        for s in self.shapes:
            s.shift(vel)
            
    # recursively shifts all SHAPES that are in this object and objects resting on this one
    def visual_recursive_shift(self,vel):
        self.visual_shift(vel)
            
        for obj in self.on_me:
            obj.visual_recursive_shift(vel)
            
    # recursively finds all objects resting on this one, and resting on those, etc. includes self
    def recursive_dependent_list(self):
        out = [self]
        for bod in self.on_me:
            out += bod.recursive_dependent_list()
            
        return out
        
    # returns nodes that give the bounding box around this object
    def self_shape(self,scale = [1.0,1.0]):
        return [(-self.size[0]*scale[0],-self.size[1]*scale[1]),(-self.size[0]*scale[0],self.size[1]*scale[1]),(self.size[0]*scale[0],self.size[1]*scale[1]),(self.size[0]*scale[0],-self.size[1]*scale[1])]
    
    # Define this object as 'on' other
    def is_on(self,other):
        self.resting_on = other     # self is on other
        if not self in other.on_me: # don't add if already added... this causes problemos.
            other.on_me.append(self)    # other has self resting on it
        
    # Define this object as not 'on' any object
    def is_off(self):
        if not (self.resting_on is None):
            self.vel += self.resting_on.vel
            (self.resting_on).on_me.remove(self) # remove this object from other's list of objects resting on it
            self.resting_on = None # remove other object from this one

    def destroy(self):
        self.destruct_counter = self.destruct_length
        self.corporeal = False
        self.solid = False
        for bod in self.on_me: # all objects once on this body are now not on it anymore
            bod.is_off()
            

    # interact with player (or any other object), self is assumed to be indestructable, non-bouncey, and solid
    def interact(self,player):    
        if not self.corporeal:
            return -1, None, None
        
        dim,gap = player.overlap_dim(self)
        side,converging = None,None

        if dim>-1: # overlap!
           # print(dim)
            side = 2*(player.pos[dim] > self.pos[dim]) - 1
            converging = (player.vel[dim]-self.vel[dim])*side < 0 # if player is moving towards object

           # record squeeze, remove overlap, reduce velocity in this dimension to 0
                #squeeze[dim][int(player.pos[dim] > i.pos[dim])] = i
            if self.solid: # can't pass throgh
                player.pos[dim] += side*gap
                if converging: 
                    player.vel[dim] = 0.0

        if side == -1 and dim == 1 and self.solid:
            player.is_on(self) # player above, colliding vertically, with solid object

        else: # if not colliding from above (including not colliding
            
            if player.resting_on == self: # if player was on this Body, no more!
                player.is_off()
                player.vel += self.vel #retain velocity from moving object

            if player in self.on_me:
                self.on_me.remove(player)
        
        return dim,side,converging
        
########################################################################################
   
# Class of objects that can be drawn, with nodes and coloring
class Shape: 
    
    def __init__(self,nodes,color = (0,0,0),line_color = None, line_width = 1,visible = True,z = 0):
        self.nodes = nodes
        self.color = color
        self.line_color = line_color
        self.line_width = line_width
        self.visible = visible
        self.z = z
        
    def draw(self,canvas,position,transform=identitymat): # draw if visible, transform if indicated, shift position
        if self.visible:
            draw_nodes = [tuple(np.matmul(transform,n)+position) for n in self.nodes] # position and transform nodes
            if not self.color is None: # if filled
                pygame.draw.polygon(canvas, self.color, draw_nodes+draw_nodes[0:1])
            if not self.line_color is None: # if outlined
               # aalines(surface, color, closed, points)
                pygame.draw.aalines(canvas, self.line_color, True, draw_nodes, self.line_width) # line width is now blend

    def transform(self,transform): # transform nodes (permanently) with matrix
        self.nodes = [tuple(np.matmul(transform,n)) for n in self.nodes] 
    
    def shift(self,shift): # shift nodes (permanently) with [x,y]
        self.nodes = [tuple(np.add(shift,n)) for n in self.nodes] 

    def info(self):
        print(vars(self))
        
    def rot90(self):
        for i,n in enumerate(self.nodes):
            self.nodes[i] = np.matmul(rot90mat,n)
            
########################################################################################
   
# Class of body that moves only in a repeated pattern
class Looper(Body):
    
    # initialize, only added parameter from body is predetermined [path] (velocity comes from this)
    def __init__(self,size,path,corporeal = True, solid = True):
        super().__init__(np.array(path[0]),size,corporeal,solid,np.subtract(path[1],path[0]))   
        self.path = path
        self.path_length = len(path)
        self.path.append(path[0]) # add initial spot to the end to make derivative easy
        self.path_counter = 0
        self.last_vel = np.array([0,0],dtype='float')
        
    # move this body (along path) and adjust velocity for next step
    def move(self):
        super().move() # move like normal body
        self.last_vel = np.array(self.vel) # need to update velocity to be of FUTURE step, for collision solving.
        self.path_counter = (self.path_counter+1)%self.path_length # iterate counter
        self.vel = np.subtract(self.path[self.path_counter+1],self.path[self.path_counter]) # define new velocity
                
        
    
 