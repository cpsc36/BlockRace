import sys, os, pygame
from pygame.locals import *

MAX_RANGE = 4
CONTROLLED = 0
map = \
"""
1111111111111111111111111111111111111111
1.....................1................1
1.....................1.............2..1
1...........111111111.1..111111111111111
1..........1111.......1................1
1..1.......1111.1111111111111...1111...1
1..........1111.......1111111..1....1..1
1..........1111111111.1111111.......1..1
1..........1111.......1111111.......1..1
1..........1111.1111111111111.....11...1
1.........11111.......1111111....1.....1
1..........1111111111.1111111....1.....1
1..........1111.......1111111..........1
1..........1111.1111111111111..........1
1..........1111.1...1...11111....1.....1
1..........1111...1...1................1
1..........11111111111111111111111111111
1......................................1
11111111111111111111111111111111111....1
1..............................11......1
1...............................1......1
1...............................1......1
1............11111111111........1......1
1......................1........1......1
1......................1........1....111
1111111111111111111....1........1......1
1....3.................1........1......1
1....3................11........1......1
1....3........1111..11111111....1......1
1....3...........1........11...........1
1....3...........11.......11...........1
1111111111111111111111111111111111111111
"""

class Player(pygame.sprite.Sprite):
   def __init__(self, team):
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.image = pygame.Surface((16, 16))
      self.image.fill((255/(team+1), 100*team, (1+team)*125))
      self.rect = self.image.get_rect(topleft=[64, 400])
      self.jump_speed = 0
      self.jumping = False
      self.entermode = 'move'
      self.box = Box([-1000,-1000], team)
      self.boxposud = 0
      self.boxposrl = 0
      self.delay = 0
      self.jdelay = 0
      self.team = team
      self.key = pygame.key.get_pressed()
   def updateKeys(self, keystate):
      self.key = keystate
   def update(self):
      dir = 0
      self.delay += 1
      self.jdelay += 1
      
      if self.key[K_SPACE]:
         if self.jdelay > 20:
            if self.jumping == False:
               if self.entermode == 'move':
                  self.jump_speed = -5.5
                  self.jumping = True
                  self.jdelay = 0
      if self.key[K_a]:
               if not self.jumping:
                  if self.delay > 5:
                     self.entermode = 'set'
                     self.delay = 0

      #Move left/right
      if self.entermode == 'move':
         if self.key[K_LEFT]:
            dir = -1#*(len(players.sprites()))
         if self.key[K_RIGHT]:
            dir = 1#*(len(players.sprites()))
      if self.entermode == 'set':
         if self.key[K_LEFT]:
            if abs(self.boxposud) + abs(self.boxposrl-1) < MAX_RANGE:
               if self.delay > 5:
                  self.boxposrl -= 1
                  self.delay = 0
         if self.key[K_RIGHT]:
            if abs(self.boxposud) + abs(self.boxposrl+1) < MAX_RANGE:
               if self.delay > 5:
                  self.boxposrl += 1
                  self.delay = 0
         if self.key[K_UP]:
            if abs(self.boxposud-1) + abs(self.boxposrl) < MAX_RANGE:
               if self.delay > 5:
                  self.boxposud -= 1
                  self.delay = 0
         if self.key[K_DOWN]:
            if abs(self.boxposud+1) + abs(self.boxposrl) < MAX_RANGE:
               if self.delay > 5:
                  self.boxposud += 1
                  self.delay = 0
         if self.key[K_s]:
            self.entermode = 'move'
       
      if self.entermode == 'set':
         self.box.rect.x = -10
         self.box.rect.y = -10
         self.box = Box([self.rect.x + (self.boxposrl*16), self.rect.y + (self.boxposud*16)], self.team)

      #Increase the jump speed so you fall
      if self.jump_speed < 5:
         self.jump_speed += 0.3
       
      #We fell off a platform!
      if self.jump_speed > 2:
         self.jumping = True
         #print self.jump_speed
      self.move(2 * dir, self.jump_speed)

   def __move(self, dx, dy):
      #Create a temporary new rect that has been moved to dx and dy
      new_rect = Rect(self.rect)
      new_rect.x += dx
      new_rect.y += dy
       
      #loop through all the sprites we're supposed to collide with
      #(collision_sprites is defined in the main() function below)
      for sprite in self.exit_sprites:
         if new_rect.colliderect(sprite.rect):
            print "You win!"
            pygame.quit()
            os._exit(1)
      for sprite in self.collision_sprites:
          
         #If there's a collision between the new rect (the one that's
         #been moved) and the sprite's rect then we check
         #for what direction the sprite is moving, and then we
         #clamp the "real" rect to that side
         if new_rect.colliderect(sprite.rect):
            #Check the X axis
            if dx > 0: #moving right
               self.rect.right = sprite.rect.left
            elif dx < 0: #moving left
               self.rect.left = sprite.rect.right
            
            #Check the Y axis
            if dy > 0: #moving down
               self.rect.bottom = sprite.rect.top
                
               #Landed!
               self.jump_speed = 0
               self.jumping = False
            elif dy < 0: #moving up
               self.rect.top = sprite.rect.bottom
               self.jump_speed = 0 #oww, we hit our head
             
            #Break the function so we'll skip the line below
            return

      for sprite in self.box_sprites:
         #if sprite is not self.box:   #Can't use own box, might be useful later.
         if sprite is self.box and self.entermode == 'set':
            pass
         elif sprite.team is not self.team:
            pass
         else:
            if new_rect.colliderect(sprite.rect):
               if dx > 0: #moving right
                  self.rect.right = sprite.rect.left
               elif dx < 0: #moving left
                  self.rect.left = sprite.rect.right
               
               if dy > 0: #moving down
                  self.rect.bottom = sprite.rect.top
                   
                  self.jump_speed = 0
                  self.jumping = False
               elif dy < 0: #moving up
                  self.rect.top = sprite.rect.bottom
                  self.jump_speed = 0 #oww, we hit our head
               return
       
      #If there's no collision, move the rect!
      self.rect = Rect(new_rect)

   #Calls __move for the X and Y axises
   def move(self, dx, dy):
      if dx != 0:
         self.__move(dx, 0)
      if dy != 0:
         self.__move(0, dy)

#Class for the temp box
class Box(pygame.sprite.Sprite):
   def __init__(self, pos, team):
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.image = pygame.Surface((16, 16))
      self.image.fill((200/(team+1), 50+(team+1)*50, 50*team))
      self.rect = self.image.get_rect(topleft=pos)
      self.team = team

#class for the gate
class Gate(pygame.sprite.Sprite):
   def __init__(self,pos):
      pygame.sprite.Sprite.__init__(self,self.groups)
      self.image = pygame.Surface((16,16))
      self.image.fill((50,50,50))
      self.rect = self.image.get_rect(topleft=pos)
   def kill(self):
      self.rect.x, self.rect.y = -10,-10

#class for the exit
class Exit(pygame.sprite.Sprite):
   def __init__(self,pos):
      pygame.sprite.Sprite.__init__(self,self.groups)
      self.image = pygame.Surface((16,16))
      self.image.fill((50,200,50))
      self.rect = self.image.get_rect(topleft=pos)
          
#Class for the white platforms
class Platform(pygame.sprite.Sprite):
   def __init__(self, pos):
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.image = pygame.Surface((16, 16))
      self.image.fill((255, 255, 255))
      self.rect = self.image.get_rect(topleft=pos)

#Create some groups. I like to use OrderedUpdates
sprites = pygame.sprite.OrderedUpdates()
players = pygame.sprite.OrderedUpdates()      
platforms = pygame.sprite.OrderedUpdates()
boxes = pygame.sprite.OrderedUpdates()
exits = pygame.sprite.OrderedUpdates()
gates = pygame.sprite.OrderedUpdates()

#Set the sprites' groups
Player.groups = sprites, players
Platform.groups = sprites, platforms
Box.groups = sprites, boxes
Exit.groups = sprites, exits
Gate.groups = sprites, gates, platforms

#The player will loop through all the sprites contained in this
#group, and then collide with them.
Player.collision_sprites = platforms
Player.box_sprites = boxes
Player.exit_sprites = exits

def parse_level():
   #Parse the level
   x, y = 0, -3
   for row in map.split("\n"):
      for char in row:

         #Spawn a platform if the character is a 1
         if char == "1":
            Platform([x*16, y*16])
         if char == "2":
            Exit([x*16, y*16])
         if char == "3":
            Gate([x*16, y*16])
 
         #Update the read position.
         x += 1
      x = 0
      y += 1
