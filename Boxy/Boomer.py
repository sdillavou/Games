from Super_Classes import Body

from Make_Sounds import boom_sound

explode_scale = 1.4
explode_delay = 3 # this many frames after destruction, explosion hits next body

explosion_size = 2.25 # For hit size # times original box size


# class for anything that explodes
class Boomer:
    
    explosion_size = explosion_size
    destruct_scale = explode_scale
    explode_delay = explode_delay
    
          
    # What happens when this explosive dies
    def explode(self): #second input not used, just to allow for polymorphism
        self.hit_box = Body(self.pos,self.size*self.explosion_size)
        boom_sound()                 # boom
        
    