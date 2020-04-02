import pygame, numpy as np


#####  Useful Matrices  ################################################################

rot90mat = np.array([[0,-1],[1,0]])
identitymat = np.array([[1,0],[0,1]])

#####      Classes      ################################################################

# Superclass for any object with location and velocity. 
class Vector:
    
    # Create & initialize position (and vel)      
    def __init__(self,position=[0,0],velocity=[0,0]): 
        self.pos = np.array(position)
        self.vel = np.array(velocity)
    
    # Move and rotate this object
    def move(self):
        self.pos = self.pos + self.vel # add vel to pos
    
    # print info (for debugging)
    def info(self):
        print(vars(self))
        
########################################################################################

# Class with size, transformation, visible, corporeal, and solid, and shapes to draw
class Body(Vector): 
    
    transform = np.copy(identitymat) # transformation matrix, can change orientation, flip, and scale.       
    shapes = []                      # dictonary of shapes to draw
    
    # Create & initialize any specified variables  
    def __init__(self,position,size,corporeal=True,solid=True,velocity=[0,0]):     
        super().__init__(position,velocity)
        self.corporeal = corporeal             # can this object interact with others
        self.solid = solid                     # this object cannot pass through others
        self.size = np.array(size)             # rectangular size of this object (width/2, height/2)

    # Modify self.transform to change size, orientation, reflection
    def rot90(self,times = 1): # rotates body 90 degrees counter clockwise
        self.transform = np.matmul(np.linalg.matrix_power(rot90mat,times),self.transform)
    def flipud(self): # flips body up and down (from its current state)
        self.transform[1,:] *= -1
    def fliplr(self): # flips body left and right (from its current state)
        self.transform[0,:] *= -1
    def scale(self,multiple): # scales body by multiple (or x and y if multiple is length 2)
        if len(multiple) == 1:
            self.transform *= multiple
        elif len(multiple) == 2:
            for i in range(2):
                self.transform[i,:] *= multiple[i]
        else:
            raise NameError('multiple is incorrect length')
    def return_to_size(self): # returns to original scale
        self.transform /= np.linalg.det(self.transform)
    def return_to_upright(self): # returns to original orientation
        self.transform = identitymat*np.linalg.det(self.transform)
        
        
    def sort_shapes(self):
        self.shapes = sorted(self.shapes, key= lambda x: x.z, reverse=False)
        
    # Draw Body's shapes, subject to position and transformation of the Body, in the order of their .z parameter
    def draw(self,canvas):        
        for s in self.shapes:
            s.draw(canvas,self.pos,self.transform)
    
        
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
                pygame.draw.polygon(canvas, self.line_color, draw_nodes+draw_nodes[0:1], self.line_width)

    def transform(self,transform): # transform nodes (permanently) with matrix
        self.nodes = [tuple(np.matmul(transform,n)) for n in self.nodes] 

        
########################################################################################
   

        
        
    
 