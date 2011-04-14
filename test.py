#! /usr/bin/env python

import os, sys, socket, threading, Queue, time

from gameClasses import *
from networkClasses import *

try:
   import cPickle as pickle
except:
   import pickle

try:
   import pygame
   from pygame.locals import *
except:
   print "Y U NO HAVE PYGAME????"

def main():
   print "Starting main"

   # Set up socket for connecting
   con_sock = socket.socket()
   con_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
   con_sock.connect((HOST,7777))

   # Socket for sending frames to client
   recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
   recv_sock.bind((HOST,SEND_PORT))

   print "Connected to server"

   print "Main loop"

   try:
      while True:
         toSend = pickle.dumps("testing!")
         con_sock.send("testing!")
         recv_sock.sendto(toSend, (HOST,RECV_PORT))
         time.sleep(0.5)
   except:
      os._exit(1)

if __name__ == '__main__':
   main()
