# Standard modules
import numpy as np
import math, copy, numpy as np
from random import randint

# Custom 
import Box, Platform, Baddie, Gettables
from Constants import box_size, S, floor,display_size, G, platform_color, sky, gettable_size
from Boomer import Boomer
from Make_Sounds import thud_sound

white = (255,255,255)
background_speed = 7.0/8.0


class Level:
    
    # small shifts used to shake the screen
    shifts = [np.array([randint(-10,10)/5,randint(-10,10)/5]) for _ in range(5)]

    
    def add_scenery(self,theme='clouds'):
        
        if theme == 'clouds':
             for k in range(0,100,10):
                    for j in range(2):
                        p = Platform.Platform([((k-50)*100*S + 50*randint(-10,10))*S,40*S+ (j*40 + randint(-15,15))*S],[4*randint(5,20)*S,randint(5,20)*S],color = white)
                        p.solid= False
                        p.corporeal = False
                        self.scenery.append(p)

    
    def __init__(self,num=0):

        self.ticker = -1
        self.sky = sky
        self.scenery = []
        self.add_scenery('clouds')
        
        self.foreground_list = [] 
        self.master_platform_list = []
        self.master_box_list = []
        self.background_list = []
        self.master_gettable_list = []
        self.baddie_list = []
        self.master_baddie_list = []
        
        self.boxes_killed = 0
        
        # default starting position
        self.player_start = np.array([0,floor-300*S],dtype=float)

        if num == 0:
            pass
          
            
        elif num == 1:

            self.player_start = np.array([200*S,floor-300*S],dtype=float)
            
            for k in range(3):
                self.add_box('metal',[17+k,0])
                
            self.add_box('protection',[0,0])
            self.add_box('tnt',[0,3],True)
            self.add_box('tnt',[1,0])
            self.add_box('nitro',[2,0])
            self.add_box('nitro',[3,0])
           # self.add_box('protection',[1,3])
            self.add_box('protection',[1,1])
            self.add_box('metal_wood',[2,1])
            self.add_box('metal',[3,1])
            self.add_box('nitro',[2,4],True)
            
            self.add_box('checkpoint',[12,1],True)
            self.add_box('wood',[15,1],True)
            self.add_box('bouncey_wood',[16,2],True)
            self.add_box('bouncey_wood',[16,3])
            
            
            self.add_box('life',[13,3],True)
            
            self.add_get('life',[14,3])
            self.add_get('protection',[15,3])
            self.add_get('fruit',[14,4])
            
            self.add_floor(-1,4)
            self.add_floor(12,20)
                
  
            self.add_rotation_platform([8,0],radius=2,platform_width=1,T=600,color=(50,50,50))

         
            
            self.master_baddie_list.append(Baddie.Owl([[box_size*2,box_size*4],[box_size*10,box_size*4]]))
            self.master_baddie_list.append(Baddie.Owl([[box_size*20,box_size*4],[box_size*12,box_size*4]]))

            
          #  for k in range(1,10):
          #      self.master_gettable_list.append(Fruit(a.pos + [600*S+box_size*2*k,-3*2*box_size]))

           
        
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
    
    def level_set(self):
        self.master_platform_list = copy.deepcopy(self.platform_list)
        self.master_box_list = copy.deepcopy(self.box_list)
        self.master_gettable_list = copy.deepcopy(self.gettable_list)
        self.master_baddie_list = copy.deepcopy(self.baddie_list)

        
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
    
        # move all non-corporeal objects to the foreground, deal with new checkpoints!
        for body_list in [self.box_list, self.gettable_list, self.baddie_list]:
            for bod in body_list[::-1]: # need to go in reverse else removal of two objects doesn't work
                if not bod.corporeal:
                    body_list.remove(bod)
                    self.foreground_list.append(bod)
                    
                    # if this is a checkpoint box, player now is spawned here.
                    if isinstance(bod,Box.Checkpoint):
                        self.player_start = np.array(bod.pos,dtype=float) + [0,-box_size]
                        self.level_set() # destroyed stuff is destroyed... forever!
                        self.boxes_killed = character.current_status.counters['boxes']
                       
                    # lives can only be got once
                    if isinstance(bod,Gettables.Life) or isinstance(bod,Box.Life):
                     
                        # search for copy in appropriate master list
                        if isinstance(bod,Gettables.Life):
                            master_list = self.master_gettable_list
                            swap_box = False
                        else:
                            master_list = self.master_box_list
                            swap_box = True
                         
                        # find closest equivalent object in that master list
                        min_dist = np.inf    
                        for bod2 in master_list:
                            if type(bod) == type(bod2):
                                dist = np.linalg.norm(bod2.pos-bod.pos)
                                if dist<min_dist:
                                    same_obj = bod2
                                    min_dist = dist
                        
                        # remove it!
                        master_list.remove(same_obj)
                        
                        # if it's a box replace it with a regular wooden box
                        if swap_box:
                            self.master_box_list.append(Box.create_box('wood',1.0*same_obj.pos,same_obj.floating))
                            

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
        for boom in self.foreground_list: # this is list of dying things, very short
            
            if character.resting_on is boom: # can't rest on an explosion, buddy
                character.is_off()
            
            # if this is a boom_box that blew up at least a few frames ago
            if isinstance(boom,Boomer) and boom.destruct_counter <= (boom.destruct_length-boom.explode_delay): 
               
                # check for anything nearby
                for bod in self.box_list+self.baddie_list+self.gettable_list: 
                    
                    if bod.corporeal and boom.hit_box.overlap(bod): # it hits one of these bad boys and they're unexploded
                        bod.destroy() # no goodies tho (false is default)
                     
                
                # also if it hits the character, get it!
                if boom.hit_box.overlap(character): 
                    character.get_hit() # multiple hits fine, character is invulnerable after one
                    
     
    # Add box to the level, position is scaled by box_size*2 and starting at floor.
    def add_box(self,box_type,position,floating=False):
        
        position[1]*=-1.0
        pos = np.array(position,dtype='float')*(box_size*2.0) + [0,floor-box_size]
        self.master_box_list.append(Box.create_box(box_type,pos,floating))           
     
    # Add gettable to the level, position is scaled by box_size*2 and centered at floor+box_size.
    def add_get(self,get_type,position):
        
        position[1]*=-1.0
        pos = np.array(position,dtype='float')*(box_size*2.0) + [0,floor-box_size]
        self.master_gettable_list.append(Gettables.create_get(get_type,pos))
        
    # Add platform to the level, position is scaled by box_size*2. Height is floor.
    def add_floor(self,start,stop,color=platform_color,line_color = (0,0,0),line_width=2): 
        self.master_platform_list.append(Platform.Platform([(start+stop)*box_size,floor+50*S],[(stop-start+1)*box_size,50*S],color,line_color,line_width))
        
    # Adds two moving platforms that rotate circularly around a specified center point
    def add_rotation_platform(self,position,radius = 2,platform_width=1,T=600,color=(50,50,50)):
   
        height = 10*S
        R = radius*box_size*2
        width = platform_width*box_size*2
        # top will be at same level as floor for position[1] = 0
        pos = np.array(position,dtype='float')*(box_size*2.0) + [0,floor+height] 
        path = [np.array([pos[0]+ R*math.cos(2*math.pi*x/T),pos[1]+ R*math.sin(2*math.pi*x/T)]) for x in range(T)]
        self.master_platform_list.append(Platform.Moving_Platform([width,height],copy.copy(path),color=color))
        self.master_platform_list.append(Platform.Moving_Platform([width,height],path[int(T/2):]+path[:int(T/2)],color=color))

        self.background_list.append(Platform.Platform(pos,[height,height]))


        
