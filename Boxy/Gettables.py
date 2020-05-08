import pygame, copy, math, numpy as np
from Super_Classes import Body, Shape
from Constants import S, gettable_size, protector_line_color, character_color, protector_color, eye_color
from Make_Sounds import fruit_sound, life_sound, protection_sound


##### Useful Identities ################################################################

#rot90mat = np.array([[0,-1],[1,0]],dtype='float')
identitymat = np.array([[1,0],[0,1]],dtype='float')


##### Useful Functions  ################################################################


##### Classes           ################################################################


# Super Class for Gettables ############################################################
class Gettable(Body): 
    
    sound = lambda x: None
    fruit = False
    lives = False
    protection = False
    
    # Initialize platform with path and color
    def __init__(self,position):
        super().__init__(position,[gettable_size,gettable_size],corporeal=True,solid=False,velocity=[0,0])  
        
        
    # make a sound and get rid of that fruit!
    def destroy(self,get_goodies=True):
        super().destroy()
        if get_goodies:
            self.sound()
    
    # resolve interaction with player
    def interact(self,player):
        if player.overlap(self):
            self.destroy()
            player.current_status.counters['fruit'] += self.fruit
            player.current_status.counters['lives'] += self.lives
            if self.protection:
                player.get_protection()
            

    
# Fruit ################################################################################
class Fruit(Gettable): 
    
    
    fruit = 1
    
    # sound to play when got
    def sound(self):
        fruit_sound()
        
        
    # Initialize platform with path and color
    def __init__(self,position):
        super().__init__(position)  
        N = 10
        nodes = [(0,-gettable_size*3/5)]+[(gettable_size*math.sin(2*math.pi*(i+int(N/10))/N),-gettable_size*math.cos(2*math.pi*(i+int(N/10))/N)) for i in range(N+1-2*int(N/10))]
        self.shapes.append(Shape(nodes,color=(255,0,0),line_color=(150,0,0),line_width=2)) # add visible shape for box

# Life #################################################################################
class Life(Gettable): 
    
    lives = 1
    
    # sound to play when got
    def sound(self):
        life_sound()
        
    # Initialize platform with path and color
    def __init__(self,position):
        super().__init__(position)  
        self.shapes.append(Shape(self.self_shape(),protector_line_color,None,line_width = 2)) 
        self.shapes.append(Shape(self.self_shape([0.9,0.9]),character_color,None,line_width = 2)) 
        self.shapes.append(Shape(self.self_shape([0.1,0.1]),eye_color,None,line_width = 2))
        self.shapes[-1].shift(self.size*[0.3,-0.3]) # eye facing one way
        self.shapes.append(Shape(self.self_shape([0.1,0.1]),eye_color,None,line_width = 2)) 
        self.shapes[-1].shift(self.size*[-0.3,-0.3]) # eye facing the other way
        
        

# Protection ###########################################################################
class Protection(Gettable): 
    
    protection = True
    
    # sound to play when got
    def sound(self):
        protection_sound()
    
    # Initialize platform with path and color
    def __init__(self,position):
        super().__init__(position)  
        self.shapes.append(Shape(self.self_shape(),protector_line_color,None,line_width = 2)) 
        self.shapes.append(Shape(self.self_shape([0.9,0.9]),protector_color,None,line_width = 2)) 
        self.shapes.append(Shape(self.self_shape([0.1,0.1]),eye_color,None,line_width = 2))
        self.shapes[-1].shift(self.size*[0.3,-0.3]) # eye facing one way
        self.shapes.append(Shape(self.self_shape([0.1,0.1]),eye_color,None,line_width = 2)) 
        self.shapes[-1].shift(self.size*[-0.3,-0.3]) # eye facing the other way
                   
          
        
#### Builder function ########################################################################

get_dict = {'fruit':Fruit, 'life':Life, 'protection':Protection}

def create_get(get_type,position):
    return get_dict[get_type](position)        