import pygame
from random import randint



#wood_bounce = pygame.mixer.Sound('wood_bounce.wav')
wood_bounce = pygame.mixer.Sound('sounds/bounce.wav')
boom = pygame.mixer.Sound('sounds/boom.wav')
boom.set_volume(2)
#wood_break = pygame.mixer.Sound('sounds/wood_bounce.wav')
#wood_break.set_volume(0.5)
slide = pygame.mixer.Sound('sounds/slide.wav')
slide.set_volume(0.3)


wood_break= [pygame.mixer.Sound('sounds/box_break'+str(i)+'.wav') for i in range(7)]


def wood_bounce_sound():
    pygame.mixer.Sound.play(wood_bounce)
    
def boom_sound():
    pygame.mixer.Sound.play(boom)

def wood_break_sound():
    pygame.mixer.Sound.play(wood_break[randint(0,6)])
    
def slide_sound():
    
    pygame.mixer.Sound.play(slide)