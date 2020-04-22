import pygame

class Keyboard:

    # set keys to false
    def __init__(self):

        self.reset()
        
    def reset(self):
        self.left_key = False
        self.right_key = False
        
        self.jump_key = False   #instantaneous
        self.jump_hold = False  #hold
        
        self.flop_key = False   #instantaneous
        self.crouch_key = False #hold

        self.attack_key = False #instantaneous
        
        self.crashed = False
    
    
    
    # take event as input, change keys as required
    def handle_in_game_events(self,event_list):

        # these flags only true if pressed in this frame
        self.jump_key = False
        self.attack_key = False
        self.flop_key = False

        # handle each individual event
        for event in event_list: 
            if event.type == pygame.KEYDOWN:
                
                # arrow keys
                if event.key == pygame.K_LEFT:
                    self.left_key = True
                elif event.key == pygame.K_RIGHT:
                    self.right_key = True

                elif event.key == pygame.K_c:
                    self.crouch_key = True
                    self.flop_key = True

                elif event.key == pygame.K_x:
                    self.jump_key = True
                    self.jump_hold = True

                elif event.key == pygame.K_z:
                    self.attack_key = True

                elif event.key == pygame.K_q:
                    self.crashed = True

            elif event.type == pygame.KEYUP:
                
                # arrow keys
                if event.key == pygame.K_LEFT:
                    self.left_key = False
                elif event.key == pygame.K_RIGHT:
                    self.right_key = False
                    
                # release holds
                elif event.key == pygame.K_c:
                    self.crouch_key = False
                elif event.key == pygame.K_x:
                    self.jump_hold = False

                
    