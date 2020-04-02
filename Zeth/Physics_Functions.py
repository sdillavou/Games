import math
import Prism from Body_Classes.py


########################################################################################

def overlapping(thing1: Prism, thing2: Prism)
    #returns true if two prisms are overlapping
    return all(abs(i-j) < (n+m) for i,j,n,m in zip(thing1.pos,thing2.pos,thing1.size,thing2.size))

def overlapping(thing1: Sphere, thing2: Sphere)
    #returns true if two spheres are overlapping
    return sum((i-j)**2 for i,j in zip(thing1.pos,thing2.pos)) < (thing1.r+thing2.r)

        
    
 