#!/usr/bin/python
from Tkinter import *
import thread
import socket

# CONFIG
port = 4220
timeBetweenPing = 120

# DO NOT CHANGE
clients = [ ]

def getIPs(chatroom, startip):
	# try to connect to the start ip
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try: 
		s.bind(("", port))
		s.sendto("get ip " + chatroom, (startip, port))
		
		endWhileCommand = False
		# get ips
		while endWhileCommand == False:
			data, addr = s.recvfrom(1024)
			# check that the message comes from the ip server
			if addr[0] == startip:
				# end command
				if "put ip finished" in data:
					endWhileCommand = True
				# ip
				else:
					clients.append(data)
	finally:
		s.close()

def sendMessage():
	for ip in clients:
		formatmsg = "put msg {0}".format(str(entry.get()))
		s.sendto(formatmsg, (ip, port))
		print formatmsg
	
def startChat():
	while True:
		data, addr = s.recvfrom(1024)
		
		# message
		if data[0:7] == "put msg":
			message = "<{0}> {1}".format (str(addr[0]), str(data[8:len(data)]))
			messages.insert(END, message)
			
		# state
		elif data[0:9] == "put state":
			# online
			if data[10:len(data)] == "online":
				chatuser.add(addr[0])
				# check for the ip in the client dictionary
				if clients[addr[0]] == False:
					clients.append(addr[0])
				
		# get ips
		elif data[0:6] == "get ip":
			# check the chatroom
			if data[7:len(data)] == chatroom:
				for ip in clients:
					s.sendto(ip, (addr[0], port))
				s.sendto("put ip finished", (addr[0], port))

def makeGui():
	root = Tk()
	
	global chatuser, messages, entry
	
	chatuser = Listbox(root)
	
	messages = Listbox(root)
	
	entry = Entry(root)
		
	send = Button(root, text="Senden", command=sendMessage)
	
	chatuser.grid(row=0, column=1)
	messages.grid(row=0, columnspan=2, column=2)
	entry.grid(row=1, column=1)
	send.grid(row=1, column=2)
	
	root.mainloop()

if __name__ == "__main__":
	
	# ask for a room
	chatroom = raw_input("Chatraum: ")
	# get ips
	startip = raw_input("Start-IP: ")
	# start getting ips for the room
	getIPs(chatroom, startip)
	
	
	# start the listening
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(("", port))
	
	# send your presence to the clients
	count = 0
	for ip in clients:
		try:
			s.sendto("put state online", (ip, port))
		except:
			del(clients[count])
		count = count + 1
	
	# start waiting for messages
	thread.start_new_thread(startChat,())
	
	# make the TKInter-GUI
	makeGui()
