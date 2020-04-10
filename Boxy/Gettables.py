import pygame, copy, math, numpy as np
from Super_Classes import Body, Shape
from Constants import S

##### Useful Identities ################################################################

#rot90mat = np.array([[0,-1],[1,0]],dtype='float')
identitymat = np.array([[1,0],[0,1]],dtype='float')


##### Useful Functions  ################################################################


##### Classes           ################################################################

    
# Fruit
class Fruit(Body): 
    
    # Initialize platform with path and color
    def __init__(self,position):
        x = 10.0*S
        super().__init__(position,[x,x],corporeal=True,solid=False,velocity=[0,0])  
        N = 50
        nodes = [(0,-x*3/5)]+[(x*math.sin(2*math.pi*(i+int(N/10))/N),-x*math.cos(2*math.pi*(i+int(N/10))/N)) for i in range(N+1-2*int(N/10))]
        
        
        #nodes = [(0,-x/2),(x/4,-3*x/4),(3*x/4,-3*x/4),(x,-2*x/4),(3*x/4,2*x/4),(2*x/4,3*x/4),(-2*x/4,3*x/4),(-3*x/4,2*x/4),(-x,-2*x/4),(-3*x/4,-3*x/4),(-x/4,-3*x/4)]
        
        self.shapes.append(Shape(nodes,color=(255,0,0),line_color=(150,0,0),line_width=2)) # add visible shape for box
