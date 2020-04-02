# import pygame, numpy as np
from Super_Classes import Body, Shape

##### Useful Identities ################################################################

#rot90mat = np.array([[0,-1],[1,0]])
#identitymat = np.array([[1,0],[0,1]])
box_size = 30

metal_color = (159,161,163)
wood_color = (200,100,0)
nitro_color = (0,200,0)
tnt_color = (200,0,0)


##### Useful Functions  ################################################################

# outputs nodes for a rectangle of given width/2 and height/2, centered at (0,0)
def rect_shape(w,h):
    return [(-w,-h),(-w,h),(w,h),(w,-h)]

##### Classes           ################################################################


# Superclass for all box types, defines size
class Box(Body): 
    
    destruct_counter = -1
    
    # Initialize box with location and color
    def __init__(self,position,color,line_color = None):   
        super().__init__(position,[box_size,box_size],True,True,[0,0])              
        self.shapes['Face'] = Shape(rect_shape(self.size[0],self.size[1]),color,line_color = line_color) # add visible shape for box
        
    def destruct(self):
        if destruct_counter == -1:
            destruct_counter = 10
            self.corporeal = False
            self.solid = False
        
# Class for metal boxes
class Metal(Box):
    # Initialize metal box
    def __init__(self,position):
        super().__init__(position,metal_color,line_color = (0,0,0))

# Class for wooden boxes
class Wood(Box):
    # Initialize wood box
    def __init__(self,position):
        super().__init__(position,wood_color,line_color = None)

    
    
# Class for nitro boxes
class Nitro(Box):
    # Initialize wood box
    def __init__(self,position):
        super().__init__(position,nitro_color,line_color = None)

 
    
    