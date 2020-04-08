import pygame



wood_bounce = pygame.mixer.Sound('wood_bounce.wav')
wood_break = pygame.mixer.Sound('wood_break.wav')
slide = pygame.mixer.Sound('slide.wav')
slide.set_volume(0.5)


def wood_bounce_sound():
    pygame.mixer.Sound.play(wood_bounce)

def wood_break_sound():
    pygame.mixer.Sound.play(wood_break)
    
def slide_sound():
    
    pygame.mixer.Sound.play(slide)