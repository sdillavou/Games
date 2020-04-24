# Standard modules
import numpy as np
import math, copy, numpy as np
from random import randint

# Custom 
import Box, Platform
from Gettables import Fruit
from Constants import box_size, S, floor,display_size
from Make_Sounds import thud_sound

white = (255,255,255)
background_speed = 7.0/8.0



class Level:
    
    # small shifts used to shake the screen
    shifts = [np.array([randint(-10,10)/5,randint(-10,10)/5]) for _ in range(5)]

    def __init__(self,num=0):

        self.ticker = -1
        
        if num == 0:

            self.scenery = []
            #self.background_list = []
            #self.master_platform_list = []
            #self.master_box_list = []
            self.foreground_list = [] 


            R = box_size*4
            N = 600
            path = [np.array([500*S + R*math.cos(2*math.pi*x/N),floor + R*math.sin(2*math.pi*x/N)]) for x in range(N)]
            d1 = Platform.Moving_Platform([box_size*2,box_size/3],copy.copy(path),color=(50,50,50),line_color = None ,line_width = 2)
            d2 = Platform.Moving_Platform([box_size*2,box_size/3],path[int(N/2):]+path[:int(N/2)],color=(50,50,50),line_color = (0,0,0) ,line_width = 2)
            p1 = Platform.Platform([100*S,floor+50*S],[200*S,50*S])
            p2 = Platform.Platform([1000*S,floor+50*S],[300*S,50*S])

            p0 = Platform.Platform(*[[500*S,floor],[10*S,10*S]])
            p0.solid = False
            p0.corporeal = False


           
            a = Box.Nitro(p1.pos - [-box_size*100/30,p1.size[1]+box_size])
            a1 = Box.Metal(a.pos - [0,box_size*2])
            a2 = Box.Nitro(a.pos - [box_size*2,0])
            a3 = Box.Metal_Wood(a.pos - [box_size*2,box_size*2])
            b2 = Box.Bouncey_Wood(path[int(N/2)]-[0,box_size+d1.size[1]])
            b3 = Box.Metal_Wood(path[int(N/2)]-[0,box_size*3+d1.size[1]])
            b4 = Box.Wood(path[int(N/2)]-[0,box_size*5+d1.size[1]])
            
            a0 = Box.Tnt(a2.pos - [box_size*2,0])
            a01 = Box.Protection(a0.pos - [0,box_size*2])
            
            
            a00 = Box.Protection(a0.pos - [box_size*2,0])
            
            
            a001 = Box.Tnt(a0.pos - [box_size*2,box_size*6])
            a001.floating = True
            
            f = Fruit(a0.pos - [box_size*2,box_size*8])


            self.master_platform_list = [p1,p2,d1,d2]
            self.master_box_list = [a001,a00,a0,a01,a,a1,a2,a3,b2,b3,b4]
            self.background_list = [p0]


            for k in range(0,100,10):
                for j in range(2):

                    p = Platform.Platform(*[[((k-50)*100 + 50*randint(-10,10))*S,40+ (j*40 + randint(-15,15))*S],[4*randint(5,20)*S,randint(5,20)*S]],color = white)
                    p.solid= False
                    p.corporeal = False
                    self.scenery.append(p)


            for k in range(4):
                for i in range(3):
                    if i == 0:
                        self.master_box_list.append(Box.Metal_Wood(a.pos + [600*S+box_size*2*k,-i*2*box_size]))
                    else:
                        self.master_box_list.append(Box.Wood(a.pos + [600*S+box_size*2*k,-i*2*box_size]))
                        
            self.master_box_list.append(Box.Tnt(a.pos + [600*S,-3*2*box_size]))

                        
                        
            for i in [0,3.0]:
                self.master_box_list.append(Box.Bouncey_Wood(a.pos + [600*S+box_size*2*6,-(i+1)*2*box_size]))
                self.master_box_list[-1].floating = True  

            self.master_gettable_list = []

            for k in range(1,10):
                self.master_gettable_list.append(Fruit(a.pos + [600*S+box_size*2*k,-3*2*box_size]))

            self.master_gettable_list.append(f)
            
            self.player_start = [200*S,floor-300*S]
            self.baddie_list = []
            self.master_baddie_list = []
        else:
            
            self.scenery = []
            self.background_list = []
            self.master_platform_list = []
            self.master_box_list = []
            self.foreground_list = [] 
            self.master_gettable_list = []
            self.player_start = [0.0,0.0]
            self.baddie_list = []
            self.master_baddie_list = []
            
        
    # Reset the level by copying master lists and clearing the foreground, then letting objects settle   
    def reset(self):
        
        # set all appropriate lists
        self.platform_list = copy.deepcopy(self.master_platform_list)
        self.box_list = copy.deepcopy(self.master_box_list)
        self.gettable_list = copy.deepcopy(self.master_gettable_list)
        self.baddie_list = copy.deepcopy(self.master_baddie_list)
        self.foreground_list = []
        self.big_list = [self.background_list, self.platform_list, self.box_list, self.gettable_list, self.baddie_list, self.foreground_list]

        # let objects find what they're resting on
        self.move_objects(land_sound_flag=False) # silently let things find their place before the curtain rises
        
        
    # Move all objects in level (everything but player and protector). Falling solid bodies can find new resting spots. 
    def move_objects(self,land_sound_flag=True):

            
     ## link all boxes to platforms they are standing on
        for bod in self.box_list:
            bod.move() # boxes not floating and not resting on will accelerate down
            if bod.vel[1] >0: # if falling 
                
                for bod2 in self.platform_list+self.box_list: # find a landing spot
                    if Box.resolve_fall(bod,bod2):
                        
                        # if not just touching another falling box, you've landed bud.
                        if not isinstance(bod2,Box.Box) or bod2.vel[1] == 0:
                            
                            bod.vel[1] = 0   #stop falling.
                            
                            if land_sound_flag: # if this is flagged (i.e. if this is in game not resetting)
                                thud_sound() # play hitting ground sound
                                
                                # tnt boxes start timers if hitting the ground or getting hit (not on reset though)
                                for b in bod.recursive_dependent_list()+[bod2]: # the base box or anything on the falling one 
                                    if isinstance(b,Box.Tnt):
                                        if b.countdown == -1:
                                            b.start_countdown()
                                           
                            break # no need to check for any more landing spots
                            
        for bod in self.platform_list+self.baddie_list: # platforms and baddies* do not fall, they float.
            bod.move()                                                         # *for now?
            
            
            
    
    # draw scenery, all bodies, player, and status. Also remove destroyed objects, and shift destroying objects to front
    def draw_level(self,gameDisplay,screen,character):
          
        # remove unnecessary destroyed objects
        for bod in self.foreground_list[::-1]:
            if bod.destruct_counter==0: #completely destroyed!
                self.foreground_list.remove(bod)
    
        # move all non-corporeal objects to the foreground
        for body_list in [self.box_list, self.gettable_list, self.baddie_list]:
            for bod in body_list[::-1]: # need to go in reverse else removal of two objects doesn't work
                if not bod.corporeal:
                    body_list.remove(bod)
                    self.foreground_list.append(bod)

        # draw scenery (special rules for when they overlap with screen)
        for bod in self.scenery:
            if abs((screen.pos[0]-bod.pos[0])*(1.0-background_speed))<(screen.size[0]+bod.size[0]):
                bod.draw(gameDisplay,[screen.pos[0] - (character.pos[0]-bod.pos[0])*background_speed-display_size[0]/2,0])
         
        # If flop just hit the ground, reset the ticker, if currently shaking, advance the ticker.
        if self.ticker == -1 and character.flopping == (character.flop_stun-1):
            self.ticker = len(self.shifts) -1   
            thud_sound()
        elif self.ticker>=0:
            self.ticker -=1
            
        # draw all non-scenery objects
        for small_list in self.big_list[:1]+[[character]]+self.big_list[1:]:
            for bod in small_list:
                if self.ticker>=0: # shakes from flop hit
                    bod.visual_shift(self.shifts[self.ticker])
                if screen.overlap(bod):
                    bod.draw(gameDisplay,[character.pos[0]-display_size[0]/2,0])
                else: # if object is blowing up/disappearing, continue this count even off screen
                    bod.death_throws()
                    
                if self.ticker>=0: # undo shift from flop hit
                    bod.visual_shift(-self.shifts[self.ticker])
        
        # draw counters and icons at top of display
        character.current_status.draw(gameDisplay)
        
    # all objects interact with player
    def interact(self,character):
    
        for bod in self.box_list+self.platform_list+self.gettable_list+self.baddie_list:
            bod.interact(character) # see how it interacts with character
        
    # exploding Boom_Box objects destroy those around them and hit player   
    def explosions(self,character): 
        
        # handle currently exploding boxes
        for boom in self.foreground_list: 
            
            if character.resting_on is boom: # can't rest on an explosion buddy
                character.is_off()
            
            # if this is a boom_box that blew up at least a few frames ago
            if isinstance(boom,Box.Boom_Box) and boom.destruct_counter <= (boom.destruct_length-boom.explode_delay): 
               
                # check for anything nearby
                for bod in self.box_list+self.baddie_list+self.gettable_list: 
                    
                    if bod.corporeal and boom.hit_box.overlap(bod):# it hits one of these bad boys and they're unexploded
                        bod.destroy(False) # no goodies tho.
                        
                
                # also if it hits the character, get it!
                if boom.hit_box.overlap(character): 
                    character.get_hit() # multiple hits fine, character is invulnerable after one
