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
         # Edit to gather frames while it waits - double buffer to interpolate?
         frameList = []
         
         ticks = clock.tick()
         
         #while len(frameList) < 1:
         #   f= get_frame()
         #   if f is not '':
         #      frameList.append(f)
         #print "frame: ", frame, "\n"

         f = get_frame()

         # Lookup Player sprite based on address tied to frame and update
         # f[0] => originating address of frame data
         # clientDict[f[0]] => tuple containing Player sprite and connection
         # clientDict[f[0]][0] => Player sprite we desire
         # f[1] => frame data to pass into update
         # (if takes care of frames that might be relics after a client dropped)
         if f is not '':
            if f[0] in clientDict:
               clientDict[f[0]][0].updateKeys(f[1])
            #for frame in frameList:
            #   if frame[0] in clientDict:
            #      clientDict[frame[0]][0].updateKeys(frame[1])
         
         players.update()

         # Construct array of tuples (rects) to send to each client
         rectdata = []
         for p in players.sprites():
            # Create a tuple of rect data
            rectdata.append( [((p.rect.left,p.rect.top),(p.rect.width,p.rect.height)),((p.box.rect.left,p.box.rect.top),(p.box.rect.width,p.box.rect.height)),p.team] )
         put_frame(rectdata)

         line_a = font.render("Incoming: " + str(incoming.qsize()), 1, (10,10,10), (255,255,255))
         linepos_a = line_a.get_rect(topleft=(0,0))
         line_b = font.render("Outgoing: " + str(outgoing.qsize()), 1, (10,10,10), (255,255,255))
         linepos_b = line_b.get_rect(topleft=(0,20))

         screen.fill((0,0,0))
         sprites.draw(screen)
         screen.blit(line_a, linepos_a)
         screen.blit(line_b, linepos_b)
         pygame.display.flip()
      # End of game loop
   except KeyboardInterrupt:
      print "Game server interrupted by user"
      os._exit(1)
   except:
      print "Error in server's game loop"
      os._exit(1)

if __name__ == '__main__':
   main()
