from Gettables import Fruit
import Box
import pygame

##### Useful Identities ################################################################

icon_size = 25.0 # does not scale with game
icon_spacing = 8*icon_size
display_height = icon_size*1.5
font = pygame.font.Font('freesansbold.ttf', int(icon_size*1.7))
black = (0,0,0)


display_fruit = Fruit([display_height,display_height])
display_fruit.transform *= icon_size/display_fruit.size[0]
display_fruit.corporeal,display_fruit.solid = False,False
display_box = Box.Wood([display_height,display_height])
display_box.transform *= icon_size/display_box.size[0]
display_box.corporeal,display_box.solid = False,False
display_life = Box.Box([display_height,display_height],black,line_color = (20,20,20),line_width = 2)
display_life.transform *= icon_size/display_life.size[0]
display_life.corporeal,display_life.solid = False,False


##### Classes           ################################################################

class Status():
# Class for storing the current game state (e.g. lives, fruit, boxes, checkpoints, etc) 

    # common icons to all Status() objects
    display_list = {'fruit':display_fruit, 'boxes':display_box,'lives':display_life}
    display_keys = ['fruit','boxes','life']
    
###############################################################################################
    # initialize a status with life, fruit, and box counts
    def __init__(self,lives = 14, fruit = 85, boxes = 0):
        
        self.counters = {'lives':lives,'fruit':fruit,'boxes':boxes}  
        

###############################################################################################        
    # draw the status to the top of the screen, and turn fruit into lives if necessary
    def draw(self,gameDisplay):
        if self.counters['fruit'] > 99:
            self.counters['fruit'] -= 100
            self.counters['lives'] += 1

        for k,key in enumerate(self.counters.keys()):
            self.display_list[key].draw(gameDisplay,[-icon_spacing*k,0])
            text = font.render(str(self.counters[key]), True, black, None)
            textRect = text.get_rect()  
            textRect.center = (icon_spacing*k + display_height*2 + textRect[3]/2,display_height+icon_size*0.15) 
            gameDisplay.blit(text, textRect) 

       
      
       