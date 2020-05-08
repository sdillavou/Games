import numpy as np
import math

S=1.2 # global scaling 1.2
#S = 0.5
S = float(S) # doubly sure... heh

G = 0.9*S # strength of gravity
box_size = 30*S
gettable_size = 10*S

character_color = (31, 61, 12)
display_size = (int(720*S),int(405*S)) # 16:9 ratio
floor = display_size[1]*5.0/6.0


protector_color = (60,60,255)
protector_line_color = (255,255,255)
protector_size = np.array([box_size*0.5,box_size*0.5],dtype='float')
eye_color = (200,200,200)
platform_color = (100,100,100)
attack_color = (160,160,160)

sky = (205, 230, 247)



def animate_path(xy,tt,animate_length):
    
    return [ np.array( [xy[0]*math.cos(tt[0]*i*math.pi/animate_length), xy[1]*math.sin(tt[1]*i*math.pi/animate_length)], dtype ='float') for i in range(animate_length)]



spike_height = 5.0*S
approx_spike_size = 5.0*S

def rect(size,shift=[0,0]):
        return [(-size[0]+shift[0],-size[1]+shift[1]),(-size[0]+shift[0],size[1]+shift[1]),(size[0]+shift[0],size[1]+shift[1]),(size[0]+shift[0],-size[1]+shift[1])]
    

def spikey_box(size,spike_sides=[1,1,1,1]):
    
    helper = [np.array([-1.0,-1.0]),np.array([1.0,-1.0]),np.array([1.0,1.0]),np.array([-1.0,1.0]),np.array([-1.0,-1.0])]
    nodes = []
    spikey_size = np.array(size,dtype='float')*1.0 # new variable to avoid changing input size
    for i in range(2):
        spikey_size[i] -= sum(spike_sides[3-i::-2])*spike_height
    
    for side in range(4):
        nodes.append(spikey_size*helper[side])
 
        if spike_sides[side]:
            spike_num = int(2.0*spikey_size[(side)%2]/approx_spike_size/2.0)*2 +1

            half_spike = (spikey_size[side%2]*2.0)/(float(spike_num)*2.0-2.0)
            direction = (helper[side+1]-helper[side])
            step = half_spike*direction # move across this side in this direction
            add_spike = spike_height*np.array([direction[1],-direction[0]]) # way spikes jut out
            for k in range(1,spike_num):
                nodes.append(spikey_size*helper[side]+step*k+(k%2)*add_spike)
        
    return [tuple(n) for n in nodes]