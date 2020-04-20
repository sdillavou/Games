import numpy as np

S=1.4 # global scaling
#S = 0.5
S = float(S) # doubly sure... heh

G = 0.9*S # strength of gravity
box_size = 30*S

character_color = (31, 61, 12)
display_size = (1000,600)
floor = display_size[1]*5.0/6.0


protector_color = (60,60,255)
protector_line_color = (255,255,255)
protector_size = np.array([box_size*0.5,box_size*0.5],dtype='float')
eye_color = (200,200,200)
