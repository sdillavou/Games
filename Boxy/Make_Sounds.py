import pygame
from random import randint
from os import path


filepath = path.join(path.dirname(__file__), '')

#wood_bounce = pygame.mixer.Sound('wood_bounce.wav')
#wood_bounce = pygame.mixer.Sound('sounds/bounce.wav')
#wood_bounce.set_volume(0.4)
wood_bounce = pygame.mixer.Sound('wood_bounce.wav')

boom = pygame.mixer.Sound(filepath+'boom.wav')

protection = pygame.mixer.Sound(filepath+'protection.wav')

#wood_break = pygame.mixer.Sound('sounds/wood_bounce.wav')
#wood_break.set_volume(0.5)
slide = pygame.mixer.Sound(filepath+'slide.wav')
slide.set_volume(0.15)

tnt_sound = pygame.mixer.Sound(filepath+'tnt_sound2.wav')
tnt_sound.set_volume(0.5)

blip = pygame.mixer.Sound(filepath+'blip.wav')
blip.set_volume(0.4)

ouch = pygame.mixer.Sound(filepath+'ouch.wav')
ouch.set_volume(0.7)

footstep = pygame.mixer.Sound(filepath+'footstep.wav')
footstep.set_volume(0.7)

power_down = pygame.mixer.Sound(filepath+'power_down.wav')
#power_down.set_volume(0.15)


thud = pygame.mixer.Sound(filepath+'thud.wav')


wood_break= [pygame.mixer.Sound(filepath+'box_break'+str(i)+'.wav') for i in range(7)]
for i in wood_break:
    i.set_volume(0.3)

def life_sound():
    pass
    
def wood_bounce_sound():
    pygame.mixer.Sound.play(wood_bounce)
    
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
    pygame.mixer.Sound.play(tnt_sound)
    
def footstep_sound():
    pygame.mixer.Sound.play(footstep)
    