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
SEND_PORT   = 7778 # Sending frames
RECV_PORT   = 7779 # Receiving frames

# Address => (sprite, connection)
clientDict = {}

# Queues for sending/receiving data
outgoing = Queue.Queue(30)
incoming = Queue.Queue()

#*************************************
#*          Client Handler           *
#*************************************

# Handles clients who connect to the server
class clientHandler(threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)

      # TCP socket for client communication
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
      self.sock.bind((HOST,CLIENT_PORT))

      # Non-blocking socket
      self.sock.setblocking(0)

      # Lists of inputs and outputs to listen on
      self.inputs  = [self.sock]
      self.outputs = []

      # Queue for outgoing messages
      self.message_queues = {}

   def run(self):
      self.sock.listen(1)
      try:
         # Begin main loop
         while True:
            # Wait for activity on stored sockets
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)

            # Handle inputs
            for s in readable:
               if s is self.sock:
                  # A new player has connected
                  connection, client_address = s.accept()
                  print 'new connection from ', client_address
                  connection.setblocking(0)
                  self.inputs.append(connection)
                  # Give the connection a queue for data we want to send
                  self.message_queues[connection] = Queue.Queue()

                  # Create player sprite 
                  newPlayer = Player(len(players.sprites())%2) 
                  print (len(players.sprites())+1)%2
                  # Add client to dictionary
                  clientDict[client_address[0]] = (newPlayer, connection)
                  print "New connection added to dictionary: ", client_address[0]
                  # For each player in the players list
                  playerlist = players.sprites()
                  toSend = []
                  for p in playerlist:
                     toSend.append(((p.rect.left,p.rect.top),(p.rect.width,p.rect.height)))
                  toSend = pickle.dumps(toSend)
                  self.message_queues[connection].put(toSend)
                  print "Finished adding new connection"
               else:
                  data = s.recv(1024)
                  if data:
                     print "Received data!"
                     # Interpret data and operate on it
                     #message_queues[s].put(data)
                     # Add output channel for response
                     #if s not in outputs:
                     #   outputs.append(s)            
                  else:
                     # Interpret empty result as closed connection
                     address = s.getpeername()[0]
                     print "Removing ", address
                     players.remove(clientDict[address][0])
                     sprites.remove(clientDict[address][0])
                     clientDict.pop(address)
                     # Stop listening for input on the connection
                     if s in self.outputs:
                        self.outputs.remove(s)
                     self.inputs.remove(s)
                     s.close()
                     # Remove message queue
                     self.message_queues.pop(s)
            # End handling inputs

            # Handle outputs
            for s in writable:
               try:
                  next_msg = message_queues[s].get_nowait()
               except Queue.Empty:
                  # No messages waiting so stop checking for writability
                  #outputs.remove(s)
                  continue
               else:
                  # Send the message
                  s.send(next_msg)
            # End handling outputs

            # Handle exceptions
            for s in exceptional:
               print "There was a problem!"
               # Stop listening for input on the connection
               #inputs.remove(s)
               #if s in outputs:
               #   outputs.remove(s)
               #s.close()
               # Remove message queue
               #self.message_queues.pop(s)
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
   def __init__(self):
      threading.Thread.__init__(self)

      # UDP socket
      self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
      self.recv_sock.bind((HOST,RECV_PORT))

      # Socket for sending frames to client
      self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
      self.send_sock.bind((HOST,SEND_PORT))

      # Lists of inputs and outputs to listen on
      self.inputs  = [self.recv_sock]
      self.outputs = [self.send_sock]

      self.oldData = []

   def run(self):
      # Begin main loop
      while True:
         readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)

         # Handle inputs
         for s in readable:
            # Do Receive from
            data, addr = self.recv_sock.recvfrom(1024)
            address = addr[0]  
            data = pickle.loads(data)
            # Add frame to inqueue
            try:               
               incoming.put((address,data))
            except Queue.Full:
               continue
         # End handling inputs

         # Handle outputs
         for s in writable:
            # Send frame from Queue
            try:
               toSend = outgoing.get(False)
               #toSend = outgoing.get(True, 0.1)
            except Queue.Empty:
               #toSend = self.oldData
               toSend = []
            except:
               print "Problem in handling outputs"
               os._exit(1)

            # Package data to send
            if toSend != []:
               toSend = pickle.dumps(toSend)
               # Send to each client
               for addr in clientDict.keys():
                  self.send_sock.sendto(toSend, (addr,SEND_PORT))
         # End handling outputs

         # Handle exceptions
         for s in exceptional:
            print "Error when selecting"
         # End handling exceptions
      # End main loop

def put_frame(toSend):
   try:
      #frameOut.put(toSend, True, Q_TIMEOUT)
      if toSend != []:
         outgoing.put(toSend, False)
   except Queue.Full:
      pass
   except:
      pass

def get_frame():
   try:
      #toReturn = frameIn.get(True, Q_TIMEOUT)
      toReturn = incoming.get(False)
      return toReturn
   except Queue.Empty:
      return ''
   except:
      pass
      #print("Queue is empty")
