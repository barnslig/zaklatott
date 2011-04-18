#!/usr/bin/python
import wx
import wx.html
import socket
import thread
import sys
import atexit
import urllib2
import random

# CONFIG
port = 4220
timeBetweenPing = 120
webIpFinder = ["http://dev.telelo.de/ip.php"]

# DO NOT CHANGE
clients = [ ]

# the wxpython gui
class Gui(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title, size=(500, 300))
		self.messages = ""
		self.panel = wx.Panel(self)
		self.makeMeAGui()
		self.Show(True)
	
	def makeMeAGui(self):
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		# message and userlist
		musplit = self.makeMeAMessageAndUserSplitter()
		
		# input
		ipanel = wx.Panel(self.panel)
		isizer = wx.BoxSizer(wx.HORIZONTAL)
		self.newmessage = wx.TextCtrl(ipanel, style=wx.TE_PROCESS_ENTER)
		sendIt = wx.Button(ipanel, -1, "Senden")
		#bindings
		self.newmessage.Bind(wx.EVT_TEXT_ENTER, sendMessage)
		sendIt.Bind(wx.EVT_BUTTON, sendMessage)
		
		# sizer
		isizer.Add(self.newmessage, proportion=1)
		isizer.Add(sendIt, flag=wx.RIGHT)
		ipanel.SetSizer(isizer)
					
		sizer.Add(musplit, proportion=1, flag=wx.EXPAND|wx.ALL)
		sizer.Add(ipanel, flag=wx.EXPAND|wx.BOTTOM)
		self.panel.SetSizer(sizer)
	
	def makeMeAMessageAndUserSplitter(self):
		# message and userlist
		musplitter = wx.SplitterWindow(self.panel)
		# userlist
		userpanel = wx.Panel(musplitter)
		usersizer = wx.BoxSizer()
		self.usernames = wx.ListBox(userpanel)
		usersizer.Add(self.usernames, proportion=1, flag=wx.EXPAND)
		userpanel.SetSizer(usersizer)
		# messages
		messagespanel = wx.Panel(musplitter)
		messagessizer = wx.BoxSizer()
		self.messagewindow = wx.html.HtmlWindow(messagespanel)
		messagessizer.Add(self.messagewindow, proportion=1, flag=wx.EXPAND)
		messagespanel.SetSizer(messagessizer)
		# split both together
		musplitter.SplitVertically(userpanel, messagespanel, sashPosition=160)
		return musplitter
		
	def rebuildUserlist(self):
		self.usernames.Clear()
		for ip in clients:
			self.usernames.Append(ip)
			
# function to get the other ips from the people in a room from an ip
def getIPs(chatroom, startip):
	# get your own ip
	ipServer = random.randrange(0, len(webIpFinder))
	f = urllib2.urlopen(webIpFinder[ipServer])
	yip = f.read()
	f.close()
	clients.append(yip)

	# check for an ip
	if len(startip) > 1:
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
	else:
		return True
	print clients
		
def startChatWaiter():
	while True:
		data, addr = s.recvfrom(1024)
		
		# message
		if data[0:7] == "put msg":
			message = "<{0}> {1}".format (str(addr[0]), str(data[8:len(data)]))
			messages = gui.messages
			gui.messages = messages + '<span style="color:orange;">&lt;{0}&gt; {1}</span><br>'.format(str(addr[0]), str(data[8:len(data)]))
			gui.messagewindow.SetPage(gui.messages + '<a name="scrolltome"></a>')
			gui.messagewindow.ScrollToAnchor("scrolltome")
			
		# state
		elif data[0:9] == "put state":
			# online
			if data[10:len(data)] == "online":
				# check for the ip in the client dictionary
				if addr[0] not in clients:
					clients.append(addr[0])
				# rebuild the user list
				gui.rebuildUserlist()
				
			# offline
			elif data[10:len(data)] == "offline":
				# get the key and delete him
				count = 0
				for ip in clients:
					if ip == addr[0]:
						del(clients[count])
					count = count + 1
				# rebuild the user list
				gui.rebuildUserlist()
		# get ips
		elif data[0:6] == "get ip":
			# check that you are in this room
			if data[7:len(data)] == chatroom:
				# return the ips
				for ip in clients:
					s.sendto(ip, (addr[0], port))
				s.sendto("put ip finished", (addr[0], port)) 
				
def sendMessage(event):
	formatmsg = "put msg {0}".format(str(gui.newmessage.GetValue()))
	for ip in clients:
		thread.start_new_thread(s.sendto, (formatmsg, (ip, port)))
	print gui.newmessage.GetValue()
	gui.newmessage.SetValue("")
				
def sendYourPresence():
	# send your presence to the clients
	count = 0
	for ip in clients:
		try:
			s.sendto("put state online", (ip, port))
		except:
			del(clients[count])
		count = count + 1
		
def stopClient():
	for ip in clients:
		s.sendto("put state offline", (ip, port))
	s.close()
	sys.exit()
			
if __name__ == "__main__":
	# ask for a room
	chatroom = raw_input("Chatraum: ")
	# get ips
	startip = raw_input("Start-IP (leave empty if you start this room): ")
	getIPs(chatroom, startip)
		
	# start listening
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(("", port))
	
	# set the exit offline message
	atexit.register(stopClient)
	
	app = wx.App()
	gui = Gui(None, -1, "zaklatott - a decentral groupchat solution")
	
	thread.start_new_thread(startChatWaiter,())
	sendYourPresence()
	
	app.MainLoop()
