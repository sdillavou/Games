import pygame, copy, numpy as np
from Super_Classes import Body, Shape, Looper

##### Useful Identities ################################################################

#rot90mat = np.array([[0,-1],[1,0]])
identitymat = np.array([[1,0],[0,1]])

metal_color = (159,161,163)
wood_color = (200,100,0)
nitro_color = (10,170,10)
tnt_color = (200,0,0)
tnt_letter_color = (230,200,50)
nitro_letter_color = (230,255,230)
platform_color = (100,100,100)



##### Useful Functions  ################################################################


##### Classes           ################################################################

    
# Moving Platforms
class Moving_Platform(Looper): 
    
    # Initialize platform with path and color
    def __init__(self,size,path,color=(50,50,50),line_color = None ,line_width = 2):   
        super().__init__(size,path,corporeal = True, solid = True)
        self.shapes.append(Shape(self.self_shape(),color,line_color,line_width)) # add visible shape for box
        

    
# Stationary Platform
class Platform(Body): 
    
    # Initialize platform with path and color
    def __init__(self,position,size,color=platform_color,line_color = None ,line_width = 2):
        super().__init__(position,size,corporeal=True,solid=True,velocity=[0,0])  
        self.shapes.append(Shape(self.self_shape(),color,line_color,line_width)) # add visible shape for box
