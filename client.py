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

HOST = '172.22.34.36'

def main():
   # Init pygame
   os.environ["SDL_VIDEO_CENTERED"] = "1"
   pygame.init()
    
   # Set the display mode
   pygame.display.set_caption("Platformer Demo")
   screen = pygame.display.set_mode((640, 480), pygame.DOUBLEBUF)
   pygame.mouse.set_visible(False)

   pygame.key.set_repeat()

   clock = pygame.time.Clock()
   
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
         clock.tick(30)

         #print pygame.time.get_ticks()
         
         # Get a frame
         frame = []
         if has_frames():
            frame = get_frame()

         # Get inputs
         for e in pygame.event.get():
            if e.type == QUIT:
               # Send exit signal over TCP
               os._exit(1)
            if e.type == KEYDOWN:
               if e.key == K_ESCAPE:
                  # Send exit signal over TCP
                  os._exit(1)
         # Send keystate over UDP
         put_frame(pygame.key.get_pressed())
         
         #print_put_frame()

         if frame != []:
            preLen = len(players.sprites())
            if len(frame) > preLen:
               Player(0)
#               Player()
            if len(frame) < preLen:
               players.remove(players.sprites()[0])
            playerlist = players.sprites()

            # Update state to display based on received data
            for i in range(len(playerlist)):
               # correct player rect with received info
               playerlist[i].rect = pygame.Rect(frame[i][0])
               playerlist[i].box.rect = pygame.Rect(frame[i][1])
               playerlist[i].team = pygame.Rect(frame[i][2])
         
         #Draw the scene
         screen.fill((0, 0, 0))
         sprites.draw(screen)
         pygame.display.flip()
      # End main loop
   except KeyboardInterrupt:
      os._exit(1)

if __name__ == '__main__':
   main()
