#! /usr/bin/env python

import sys, os, socket, threading

from gameClasses import *
from clientNetwork import *

try:
   import cPickle as pickle
except:
   import pickle

try:
   import pygame
   from pygame.locals import *
except:
   print "Pygame not found"

HOST = ''

def main():
   # Init pygame
   os.environ["SDL_VIDEO_CENTERED"] = "1"
   pygame.init()

   # Set the display mode
   pygame.display.set_caption("Platformer Demo")
   screen = pygame.display.set_mode((640, 480), pygame.DOUBLEBUF)
   pygame.mouse.set_visible(False)
   pygame.font.init()
   pygame.key.set_repeat(500, 30)

   clock = pygame.time.Clock()
   font = pygame.font.Font(None,25)
   # Groups: sprites, players, platforms, boxes, exits
   # Player.groups = sprites, players
   # Platform.groups = sprites, platforms
   # Box.groups = sprites, boxes
   # Exit.groups = sprites, exits

   # Create all the platforms by parsing the level.
   parse_level()

   # Set up network threads
   
   commH = commHandler(HOST)
   commH.setDaemon(True)
   commH.start()

   # Start threads
   clientH = clientHandler(HOST)
   clientH.setDaemon(True)   
   clientH.start()

   try:
      while True:
         #clock.tick(50) # Don't need to limit fps if it's just drawing?
         clock.tick()
         #print pygame.time.get_ticks()
         
         # Get inputs
         for e in pygame.event.get():
            if e.type == QUIT:
               # Send exit signal over TCP
               os._exit(1)
            if e.type == KEYDOWN:
               put_frame(pygame.key.get_pressed())
               if e.key == K_ESCAPE:
                  # Send exit signal over TCP
                  os._exit(1)
            if e.type == KEYUP:
               put_frame(pygame.key.get_pressed())

         line_a = font.render("Incoming: " + str(incoming.qsize()), 1, (10,10,10),(255,255,255))
         linepos_a = line_a.get_rect(topleft=(0,0))
         line_b = font.render("Outgoing: " + str(outgoing.qsize()), 1, (10,10,10),(255,255,255))
         linepos_b = line_b.get_rect(topleft=(0,20))

         #Draw the scene
         screen.fill((0, 0, 0))
         sprites.draw(screen)
         screen.blit(line_a,linepos_a)
         screen.blit(line_b,linepos_b)
         pygame.display.flip()
      # End main loop
   except KeyboardInterrupt:
      os._exit(1)

if __name__ == '__main__':
   main()
