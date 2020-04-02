import math

dim = 3
center_smash_x = True
center_smash_y = False
max_fall_speed = 8
G = 0.3 # strength of gravity 
jump_strength = 8
crouch_bonus = 0.25**2 # 25% height increase on jump (h ~ v^2)
z_proj = [0.2,0.1,-1] # shift of 1 in z corresponds to this much shift in projected view


class Body:
    # Superclass that covers geometric attributes
    
    visible = True
    
    def __init__(self,position,size,S):
    # Create & initialize location (x,y) and size (w,h)
        self.pos = [i*S for i in position]
        self.size = [i*S for i in size]
        self.vel = [0 for i in position]
        self.corporeal = False
        self.shift = [-5*S,-2*S]
        self.S = S
        self.find_ui_stack()
        
    def find_ui_stack(self):
       # z = sum((i+k)/j for i,k,j in zip(self.pos,self.size,z_proj))
        self.stack = {'front':self.pos[2]+self.size[2],'side':self.pos[2],'top':self.pos[2]} # stack for front and for sides
        
    def move(self):
    # Move this object
        self.pos = [i+j for i,j in zip(self.pos,self.vel)] # add vel to pos
        self.find_ui_stack()
        
    def is_moving(self):
    # Returns 'is this object moving'
        return any(i!=0 for i in self.vel)
        
    def overlap(self,other):
    # Returns 'is overlapping/touching other'
        return all(abs(x1-x2) <= (w1+w2) for x1,x2,w1,w2 in zip(self.pos,other.pos,self.size,other.size))
    #(abs(self.x-other.x)<=(self.w+other.w) and abs(self.y-other.y)<=(self.h+other.h))


    def info(self):
        # print info (for debugging)
        print(vars(self))
        
    def drawings(self,flag,smash):

        # 8 points that define a cube. these are projected into the (x,y) plane using z_proj
        pts = [ tuple((self.pos[0]+self.pos[2]*z_proj[0]+k*self.size[0] + i*z_proj[0]*self.size[2], self.pos[1]+self.pos[2]*z_proj[1]+j*self.size[1] +i*z_proj[1]*self.size[2])) for i in [1,-1] for j in [1,-1] for k in [-1,1] ]

        
#        # draws rectangle of object but also top and side facets to make everything look 3D
#        pts = ((self.pos[0]+self.size[0]-1, self.pos[1]+self.size[1]-1), (self.pos[0]-self.size[0]+1,self.pos[1]+self.size[1]-1), (self.pos[0]-self.size[0]+1,self.pos[1]-self.size[1]+1), (self.pos[0]+self.size[0]-1,self.pos[1]-self.size[1]+1), (self.pos[0]+self.size[0]+self.size[2]*z_proj[0]-1,self.pos[1]-self.size[1]+self.size[2]*z_proj[1]+1), (self.pos[0]-self.size[0]+self.size[2]*z_proj[0]+1,self.pos[1]-self.size[1]+self.size[2]*z_proj[1]+1), (self.pos[0]-self.size[0]+self.size[2]*z_proj[0]+1,self.pos[1]+self.size[1]+self.size[2]*z_proj[1]-1))
        

        
        x_plus,y_plus = 0,-400
        
        # make screen follow smash

        if center_smash_x:
            x_plus = 400-smash.pos[0]
        if center_smash_y:
            y_plus = 450-smash.pos[1]
        
        pts = tuple((i[0]+x_plus,i[1]+y_plus) for i in pts)
        
        # output correct set of points
        if flag == 'front': # front face
            return pts[2:4]+pts[1::-1]+pts[2:3]
        elif flag == 'top':
            return pts[-1:]+pts[6:7]+pts[2:4]+pts[-1:]
        elif flag == 'side':
            return pts[2:3]+pts[6:3:-2]+pts[0:3:2]
        else:
            raise NameError('Undefined drawing requested')
    
#######################################################
    
class Smash(Body):
# Subclass for main character   
    def __init__(self,position,S):
        super().__init__(position,[10,20,10],S)
        self.moveable = True
        self.color = (102,51,153)
        self.corporeal = True
        self.crouching = False
        self.airborne = True
        self.S = S
        self.G = G
        
    def gravity(self):
        # accelerate due to gravity
        self.vel[1] = min(max_fall_speed*self.S,self.vel[1]+self.G*self.S)
        
    def jump(self):
        # flies upward, faster if crouching, not if airborne
        if not self.airborne:
            self.vel[1] = (-jump_strength*(1+ crouch_bonus*(self.crouching>0)))*self.S
    
    def crouch(self,keyval): # makes self smaller to crouch, bigger to uncrouch
        
        if self.crouching:
            if not keyval or self.airborne: # if key released or in the air, uncrouch
                self.size[1] = 20*self.S
                self.pos[1] -= 10*self.S
                self.crouching = False
        else: # if uncrouched
            if keyval and not self.airborne: # down key pressed and on the ground
                self.size[1] = 10*self.S
                self.pos[1] += 10*self.S
                self.crouching = True
           
        
    def walk(self,keyval,keyval2): # keyval = (is right key down) - (is left key down) or (is down key down) - (is up key down)
        accel = 0.2
        decel = 200
        top_speed = 3
        
        if self.airborne:# less control in the air. duh.
            accel = 0.05
            decel = 0.1
            
        if self.crouching:# can't crawl as fast as you can run... duh.
            top_speed = 1
            
        v = self.vel[0]
        v2 = self.vel[2]
        
        if keyval == 0 or keyval*v <0:
          #  if keyval*v < 0: # active deceleration
          #      decel *=1.5
            if self.airborne:
                if abs(v)>0: # prevent decel into turning around
                    self.vel[0] = v-math.copysign(min(accel*self.S,abs(v)),v)
            else: # if on ground, stop immediately
                self.vel[0] = 0
        else:
            self.vel[0] = min(max(-top_speed*self.S,v+keyval*decel*self.S),top_speed*self.S) # prevent exceeding top speed

        if keyval2 == 0 or keyval2*v2 <0:
          #  if keyval2*v2 < 0: # active deceleration
          #      decel *=1.5
            if self.airborne:
                if abs(v2)>0: # prevent decel into turning around
                    self.vel[2] = v2-math.copysign(min(accel*self.S,abs(v2)),v2)
            else: # if on ground, stop immediately
                self.vel[2] = 0
        else:
            self.vel[2] = min(max(-top_speed*self.S,v+keyval2*decel*self.S),top_speed*self.S) # prevent exceeding top speed

    def collision(self,other):
    # Returns true if objects will collide in this next step.
    # In this case, reduce self.vel such that objects will not intersect after this step.
    # In the next iteration with self and body, self.vel[i] will be reduced to 0 by this same algorithm.
    
        if not other.corporeal:
            raise NameError('Body.collision called for an input that is non-corporeal. Use overlap instead.')
    
        dist = [i-j for i,j in zip(other.pos,self.pos)]
        spacer = [i+j for i,j in zip(other.size,self.size)]
        gap = [abs(i)-j for i,j in zip(dist,spacer)] # if overlap, gap is set to 0
        dist_sign = [math.copysign(1,i) for i in dist]
        vel = [i-j for i,j in zip(other.vel,self.vel)]
        closing_speed = [-i*j for i,j in zip(dist_sign,vel)] # positive is in direction of collision
        t = 2 #time to collision. greater than 1 means no collision
        collision_dim = -1 # dimension of collision, -1 means no collision
        
        for idx in range(dim): # for each dimension

            if closing_speed[idx] > max(gap[idx],0): # converging and will overlap in dimension [idx] (gap min is 0)
                
                t0 = max(gap[idx],0)/closing_speed[idx] # time until potential collision in this dimension
                if  t0 < t:# if not, a different direction collision already found will happen first
                    
                    other_dims = [i for i in range(dim) if i!= idx]
                    will_collide = True
                    for d in other_dims:
                        if abs((self.pos[d]+self.vel[d]*t0)-(other.pos[d]+other.vel[d]*t0))-spacer[d] > -0.001*self.S:
                            # will miss in this dimension
                            will_collide = False
                            break
                    
                    if will_collide:
                        t = t0
                        collision_dim = idx
                        
        if collision_dim >=0:
              # tell smash she's on the ground
            if collision_dim == 1 and abs(self.vel[1] - self.G*self.S) < 0.001*self.S: # gravity strength 
                self.airborne = False
                
            if any(i!=0 for i in other.vel): # if other is moving
                raise NameError('Other is moving and you havent worked out the math you bum.')
            else:
                if self.overlap(other):
                    self.vel[collision_dim] = 0 # stay put if overlapping already
                else:
                    self.vel[collision_dim] = math.copysign(gap[collision_dim],self.vel[collision_dim]) 
                    # adjust speed to just touch
            
          
                
            return collision_dim
        else:
            return collision_dim
              
        
        
class Box(Body):  
# Subclass for boxes
    def __init__(self,x,y,S):
        super().__init__([x,y,0],[16,16,16],S)
        self.moveable = False
        self.corporeal = True
        self.color = (0,0,0)
        
class WoodBox(Box):
# Subclass for wooden boxes
    color = (210,105,30)
    
    def __init__(self,x,y,S):
        super().__init__(x,y,S)
        
            
class MetalBox(Box):
# Subclass for metal boxes
    def __init__(self,x,y,S):
        super().__init__(x,y,S)
        self.color = (210,210,210)
        
                    
class NitroBox(Box):
# Subclass for metal boxes
    def __init__(self,x,y,S):
        super().__init__(x,y,S)
        self.color = (159,218,64)
        
            
class Wall(Body):   
# Subclass for walls  
    def __init__(self,x,y,w,h,S):
        super().__init__([x,y,0],[w,h,50],S)
        self.moveable = False
        self.color = (0,0,0)
        self.corporeal = True

class Fruit(Body):   
# Subclass for fruits to collect
    def __init__(self,x,y,S):
        super().__init__([x,y,0],[6,6,6],S)
        self.moveable = False
        self.color = (0.9*255,0.1*255,0.05*255)
        self.corporeal = False
        self.shift = [-1.5*S,-1.5*S]

class Baddie(Body):
# Subclass for bad guys
    def __init__(self,x,y,S):
        super().__init__([x,y,0],[20,20,20],S)
        self.moveable = False
        self.color = (0.8*255,0*255,0.8*255)
        self.corporeal = True
        
        
#######################################################

class Facet:
    
    def __init__(self,pts,color,stack):
        self.pts = pts
        self.color = color
        self.stack = stack