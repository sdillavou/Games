import pygame

# Standard modules
import numpy as np
#from time import sleep

# Custom classes and functions
from Super_Classes import Body, Shape
from Player import Player
from Constants import display_size, sky, spikey_box, attack_color, character_color,eye_color
from Level import Level
from Make_Sounds import ouch_sound, thud_sound



def build_level(num,keyboard,gameDisplay,clock):
    
   


    # Object holding all level Bodies and scenery
    level = Level(0) # 0 means generate a blank level

    # Object to determine what to draw on screen (anything non overlapping isn't drawn)
    screen = Body([level.player_start[0],display_size[1]/2],np.array(display_size)/2,corporeal=True,solid=False,velocity=[0,0])   


    #level.background_list.append(screen2)

    death_delay = 60 # time after player's death that the level keeps tickin'
    crashed = death_delay # start with a completed crash cycle to initalize everything
    paused = False


    while True: # play the game
        
        
    ##############################################################################
        # Note keyboard inputs and store them (including killing player by quitting)

        keyboard.handle_keys(pygame.event.get())

        if keyboard.crashed: # toggle pause
            paused = not paused
            keyboard.crashed = False
            if paused:
                pause_menu.draw(gameDisplay)
                gameDisplay.blit(text, textRect) 
            
            
        if not paused:

        ##############################################################################
            # Handle player death and level reset

            if crashed or character.pos[1]>(1.5*display_size[1]): # player off screen = dead!
                if crashed == death_delay:
                    character = Player(level.player_start)
                    crashed = 0
                    level.reset()
                    keyboard.reset()
                else:    
                    crashed += 1

                if crashed == 2: # just died, play ouch sound!
                    ouch_sound()



        ##############################################################################    
            # Move every non-player object and resolve their interactions, including explosions

            level.move_objects()
            level.explosions(character) # these can also affect character

        ##############################################################################
            # [if player is alive] Evolve its state, move it, and resolve interactions with other bodies

            if not crashed: # if player is dead, skip this part

                # determine player's state and velocity, then move
               # character.evolve(keyboard)
                character.move()

                # sort box_list so that closest bodies interact first: prevents e.g. diagonally breaking boxes
                level.box_list = sorted(level.box_list, key= lambda x: sum((character.pos-x.pos)**2), reverse=False)

               # squeeze = [[False,False],[False,False]]

                # all objects interact with the player (destroy boxes, get fruit, land on platforms, etc)
                level.interact(character)

                # some of these interactions might have killed ya. Then ya dead!
                if character.protection < 0:
                    crashed = 1



        ##############################################################################
            # Prepare canvas and draw visuals

            # fill display with sky color and set center position for screen (only overlapping objects will draw)
            gameDisplay.fill(sky)
            screen.pos = np.array([character.pos[0],display_size[1]/2]) # location of the center of the screen

            # move all non-corporeal objects to the foreground, draw all bodies, and clean foreground list of dead objects
            level.draw_level(gameDisplay,screen,character)

      #  sleep(0.1) # turned on for debugging
        pygame.display.update()
        clock.tick(35)

    ##############################################################################

    pygame.quit()