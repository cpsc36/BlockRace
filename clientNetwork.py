import os, sys, socket, threading, Queue, select

from gameClasses import *

try:
   import cPickle as pickle
except:
   import pickle

try:
   import pygame
   from pygame.locals import *
except:
   print "Y U NO HAVE PYGAME????"

# Default host
HOST  = ''

# Ports for:
CLIENT_PORT = 7777 # Listening for clients
SEND_PORT   = 7779 # Sending frames
RECV_PORT   = 7778 # Receiving frames

# Queues for sending/receiving data
outgoing = Queue.Queue()
incoming = Queue.Queue()
sigcomm  = Queue.Queue()

#*************************************
#*          Client Handler           *
#*************************************

# Handles clients who connect to the server
class clientHandler(threading.Thread):
   def __init__(self, server_address):
      threading.Thread.__init__(self)

      # TCP socket for client communication
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

      # Non-blocking socket
      #self.sock.setblocking(0)

      # Connect to server
      self.sock.connect((server_address,CLIENT_PORT))

      # Lists of inputs and outputs to listen on
      self.inputs  = [self.sock]
      self.outputs = [self.sock]

   def run(self):
      try:
         # Begin main loop
         while True:
            # Wait for activity on stored sockets
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)

            # Handle inputs
            for s in readable:
               data = s.recv(1024)
               if data:
                  print "Received data!"
                  # Received command from server, act on it           
               else:
                  # Interpret empty result as closed connection
                  print "Server went down!"
                  os._exit(1)
            # End handling inputs

            # Handle outputs
            for s in writable:
               try:
                  next_msg = sigcomm.get(False)
               except Queue.Empty:
                  # No messages waiting so stop checking for writability.
                  #outputs.remove(s)
                  continue
               else:
                  print >>sys.stderr, 'sending "%s" to %s' % (next_msg, s.getpeername())
                  s.send(next_msg)
            # End handling outputs

            # Handle exceptions
            for s in exceptional:
               print >>sys.stderr, 'handling exceptional condition for', s.getpeername()
               # Stop listening for input on the connection
               print "Exceptions???"
            # End handling exceptions
         # End main loop
      except:
         print "Error in client handler"
         os._exit(1)
      #End update loop

#*************************************
#*        Send/Recv Handler          *
#*************************************

# Handles sending data to clients
class commHandler(threading.Thread):
   def __init__(self, server_address):
      threading.Thread.__init__(self)

      self.server_address = server_address

      # UDP socket
      self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
      self.recv_sock.setblocking(0)
      self.recv_sock.bind((HOST,RECV_PORT))

      # Socket for sending frames to client
      self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

      # Lists of inputs and outputs to listen on
      self.inputs  = [self.recv_sock]
      self.outputs = [self.send_sock]

   def run(self):
      # Begin main loop
      while True:
         readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)
         
         # Handle inputs
         for s in readable:
            # Receive
            #data = self.recv_sock.recv(1024)
            data = s.recv(1024)
            data = pickle.loads(data)
            # Add frame to inqueue
            if data != []:
               preLen = len(players.sprites())
               if len(data) > preLen:
                  Player(data[len(players.sprites())][2])
               if len(data) < preLen:
                  players.remove(players.sprites()[0])
                  sprites.remove(players.sprites()[0].box)
               playerlist = players.sprites()

               for i in range(len(playerlist)):
                  playerlist[i].rect = pygame.Rect(data[i][0])
                  playerlist[i].box.rect = pygame.Rect(data[i][1])
         # End handling inputs

         # Handle outputs
         for s in writable:
            # Send frame from Queue
            try:
               toSend = outgoing.get(False)
            except Queue.Empty:
               # Nothing in outgoing to send
               continue
            except:
               print "Problem in handling outputs"
               os._exit(1)

            # Package data to send
            toSend = pickle.dumps(toSend)

            s.sendto(toSend, (self.server_address,SEND_PORT))
         # End handling outputs

         # Handle exceptions
         for s in exceptional:
            print "Error when selecting"
         # End handling exceptions
      # End main loop

def put_frame(toSend):
   try:
      outgoing.put(toSend, False)
   except:
      pass
      #print("Queue is full")

def get_frame():
   try:
      toReturn = incoming.get(False)
      return toReturn
   except Queue.Empty:
      return ''
   except:
      pass

def has_frames():
   if incoming.qsize() > 0:
      return True
   else:
      return False
