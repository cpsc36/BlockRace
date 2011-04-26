#! /usr/bin/env python

import sys, os, socket, threading

from gameClasses import *
from serverNetwork import *

try:
   import cPickle as pickle
except:
   import pickle

try:
   import pygame
   from pygame.locals import *
except:
   print "Y U NO HAVE PYGAME????"

#*************************************
#*         Game Logic Main           *
#*************************************

def main():
   try:
      # Set up network threads
      clientH = clientHandler()
      commH   = commHandler()
      clientH.setDaemon(True)
      commH.setDaemon(True)

      # Start network threads
      print "Starting network threads..."
      clientH.start()
      commH.start()
      print "All threads have started..."

      # Initialize pygame      
      print "Initializing pygame"
      pygame.init()
      pygame.font.init()
      clock = pygame.time.Clock()
      font = pygame.font.Font(None,25)

      pygame.display.set_caption("SERVER WINDOW")
      screen = pygame.display.set_mode((640,480), pygame.DOUBLEBUF)
      pygame.mouse.set_visible(True)

      #Create all the platforms by parsing the level.
      parse_level()

      # Begin game loop
      while True:
         clock.tick(60)
         
         players.update()

         line_a = font.render("Incoming: " + str(incoming.qsize()), 1, (10,10,10), (255,255,255))
         linepos_a = line_a.get_rect(topleft=(0,0))
         line_b = font.render("Outgoing: " + str(outgoing.qsize()), 1, (10,10,10), (255,255,255))
         linepos_b = line_b.get_rect(topleft=(0,20))
         try:
            screen.fill((0,0,0))
            sprites.draw(screen)
         except:
            # Guards against KeyError exception originating in draw
            # Not critical
            continue
            #screen.fill((0,0,0))
            #sprites.draw(screen)
         screen.blit(line_a, linepos_a)
         screen.blit(line_b, linepos_b)
         pygame.display.flip()
      # End of game loop
   except KeyboardInterrupt:
      print "Game server interrupted by user"
      os._exit(1)
   except Exception as e:
      print "Error in server's game loop"
      print type(e)
      print e
      os._exit(1)

if __name__ == '__main__':
   main()
