import math


########################################################################################


class Body:
    # Superclass of all bodies, defines geometric attributes position and velocity, and flags visible and corporeal
    
    visible = True
    corporeal = True
    
    def __init__(self,position):
    # Create & initialize location and (zero) velocity
        self.__init__(position,(0 for i in position))

    def __init__(self,position,velocity):
    # Create & initialize location and  velocity
        self.pos = list(position)
        self.vel = list(velocity)

    def move(self):
    # Move this object
        self.pos = [i+j for i,j in zip(self.pos,self.vel)] # add vel to pos
        
    def is_moving(self):
    # Returns 'is this object moving'
        return any(i!=0 for i in self.vel)

    def info(self):
        # print info (for debugging)
        print(vars(self))
        
########################################################################################
    
class Sphere(Body): 
    # This body is a sphere. How round.
    
    def __init__(self,position,radius):
    # Create & initialize location, raidus, and (zero) velocity
        super().__init__(position)
        self.r = radius

    def __init__(self,position,radius,velocity):
    # Create & initialize location and  velocity
        super().__init__(position,velocity)
        self.r = radius
        self.pos = [i for i in position]
        self.vel = [i for i in velocity]   

########################################################################################

class Prism(Body): 
    # This body is a prism. How angular.
    
    def __init__(self,position,size):
    # Create & initialize location, raidus, and (zero) velocity
        super().__init__(position)
        self.size = [i for i in size]

    def __init__(self,position,radius,velocity):
    # Create & initialize location and  velocity
        super().__init__(position,velocity)
        self.r = radius
        self.pos = [i for i in position]
        self.vel = [i for i in velocity]
        
        
########################################################################################
        
        

        
        
    
 