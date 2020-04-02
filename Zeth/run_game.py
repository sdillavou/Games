import pygame
import math
from Smash_Classes import Box, Smash, Wall, Baddie, Fruit, MetalBox, WoodBox


S = 2 # master scaling of everything

pygame.init()

display_width = 800
display_height = 600

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Smash Pangolin')

black = (0,0,0)
white = (255,255,255)

clock = pygame.time.Clock()
gameDisplay.fill(white)

    
init_x,init_y = 30,100
pangolin = Smash(init_x,init_y,S)

move_rate = 1


def show1(thing):
    # front face
    pygame.draw.polygon(gameDisplay,thing.color,thing.drawings('front',pangolin))

def show2(thing):
    # side faces
    pygame.draw.polygon(gameDisplay,tuple(i/2 +255/2 for i in thing.color),thing.drawings('top',pangolin))
    pygame.draw.polygon(gameDisplay,tuple(i/2 +255/2 for i in thing.color),thing.drawings('side',pangolin))


things = [Wall(200*2,200*2,250*2,5*2,S),
          Wall(300*2,105*2,5*2,100*2,S),
          Wall(0*2,105*2,5*2,100*2,S),
          WoodBox(50*2,180*2,S)]

for k in range(10):
    things.append(Fruit(k*20 + 200,180*2,S))
    
for i in range(5):
    things.append(WoodBox(k*20 + 400,150*2,S))
    
for i in range(4):
    things.append(MetalBox(70*2+k*20,180*2-k*4,S))

left_key = False
right_key = False
up_key = False
down_key = False

crashed = False

while not crashed:
    
    for event in pygame.event.get():

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                left_key = True
            elif event.key == pygame.K_RIGHT:
                right_key = True
                
            if event.key == pygame.K_c:
                down_key = True
        
            elif event.key == pygame.K_UP:
                pangolin.jump()
                
            elif event.key == pygame.K_q:
                crashed = True
                
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left_key = False
            elif event.key == pygame.K_RIGHT:
                right_key = False
            elif event.key == pygame.K_c:
                down_key = False
            
      #      if event.key == pygame.K_UP:
      #      elif event.key == pygame.K_DOWN:
             
        ######################
    
    gameDisplay.fill(white)
    on_floor = False
    
    # Crouch if keys are pressed
    pangolin.crouch(down_key)
    
    # Walk if keys are pressed
    pangolin.walk(right_key-left_key)
        
    # accelerate pangolin due to gravity
    pangolin.gravity()
    
    pangolin.airborne = True # will be set to false if proper collision occurs
    
    removal = [] # objects destroyed by ms. smash
    for k,i in enumerate(things):
       
        if i.corporeal: # if corporeal object (not fruit)
            
            v = pangolin.vel[1]
            dim = pangolin.collision(i) # automatically adjusts velocity within this function. collision = (dim>=0)
            
            if dim == 1 and isinstance(i,WoodBox) and abs(v)>pangolin.G*S: #and was_falling: # collision in y, box, pangolin was falling
                removal.append(i)
                i.visible = False
                pangolin.vel[1] = -math.copysign((4-(v<0))*S,v) # bounce!
            
        else: #non-corporeal, do not adjust velocity
            if isinstance(i,Fruit):
                if pangolin.overlap(i):
                   #i.color = tuple([i*.98 for i in list(i.color)])
                    removal.append(i)
                    i.visible = False
       
    
    # remove destroyed objects
    for i in removal:
        things.remove(i)
    
    # move the 
    pangolin.move()
    
    if pangolin.airborne:
        pangolin.color = (30,30,30)
    else:
        pangolin.color = (0,0,0)

    for i in [pangolin]+things:
        if i.visible:
            show2(i)
            
  
    
    for i in [pangolin]+things:
        if i.visible:
            show1(i)

        
    pygame.display.update()
    clock.tick(100)

pygame.quit()


