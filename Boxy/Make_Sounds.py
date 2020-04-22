import pygame
from random import randint



#wood_bounce = pygame.mixer.Sound('wood_bounce.wav')
#wood_bounce = pygame.mixer.Sound('sounds/bounce.wav')
#wood_bounce.set_volume(0.4)
#wood_bounce = pygame.mixer.Sound('wood_bounce.wav')
wood_bounce2 = pygame.mixer.Sound('sounds/bounce.flac')
wood_bounce2.set_volume(0.3)

boom = pygame.mixer.Sound('sounds/boom.wav')

protection = pygame.mixer.Sound('sounds/protection.wav')

#wood_break = pygame.mixer.Sound('sounds/wood_bounce.wav')
#wood_break.set_volume(0.5)
slide = pygame.mixer.Sound('sounds/slide.wav')
slide.set_volume(0.15)

blip = pygame.mixer.Sound('sounds/blip.wav')
blip.set_volume(0.7)


ouch = pygame.mixer.Sound('sounds/ouch.wav')
ouch.set_volume(0.7)

power_down = pygame.mixer.Sound('sounds/power_down.wav')
#power_down.set_volume(0.15)


thud = pygame.mixer.Sound('sounds/thud.wav')


wood_break= [pygame.mixer.Sound('sounds/box_break'+str(i)+'.wav') for i in range(7)]
for i in wood_break:
    i.set_volume(0.3)

def wood_bounce_sound():
    pygame.mixer.Sound.play(wood_bounce2)
    
def boom_sound():
    pygame.mixer.Sound.play(boom)

def wood_break_sound():
    pygame.mixer.Sound.play(wood_break[randint(0,6)])
    
def slide_sound():
    pygame.mixer.Sound.play(slide)
    
def fruit_sound():
    pygame.mixer.Sound.play(blip)
    
def thud_sound():
    pygame.mixer.Sound.play(thud)
    
def protection_sound():
    pygame.mixer.Sound.play(protection)
    
def ouch_sound():
    pygame.mixer.Sound.play(ouch)
    
def power_down_sound():
    pygame.mixer.Sound.play(power_down)
    
def countdown_sound():
    pygame.mixer.Sound.play(blip)
    