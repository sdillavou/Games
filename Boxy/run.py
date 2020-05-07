import pygame
if False:
    import pygame._view

# These must be spcified for pyinstaller for some reason.
import numpy.random.common
import numpy.random.bounded_integers
import numpy.random.entropy

pygame.init()

# Custom classes and functions
from Constants import display_size
from Level import Level
from Keyboard import Game_Keyboard
from Play_Level import play_level

# Initialize game
gameDisplay = pygame.display.set_mode(display_size)
clock = pygame.time.Clock()

# initialize keyboard object to take in control data and feed it to the player object
keyboard = Game_Keyboard()

play_level(1,keyboard,gameDisplay,clock)

pygame.quit()
