import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
if False:
    # These must be spcified for pyinstaller for some reason.
    import pygame._view
    import numpy.random.common
    import numpy.random.bounded_integers
    import numpy.random.entropy


pygame.init();

# Custom classes and functions
from Constants import display_size
from Keyboard import Game_Keyboard
from Play_Level import play_level
from Status import Status

# Initialize game
gameDisplay = pygame.display.set_mode(display_size)
clock = pygame.time.Clock()

# initialize keyboard object to take in control data and feed it to the player object
keyboard = Game_Keyboard()

play_level(1,keyboard,gameDisplay,clock,Status(lives = 15, fruit = 0, boxes = 0)) # arbitrary status start for now

pygame.quit()
