'''

# Thread to handle messages from the Server.  
class ServerMessageThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		#print_time(self.name, self.counter, 5)
		

		print (SERVER_HOST, SERVER_PORT)

		
		while (1):
		
			
			try:
				
				# Open socket and send data - Open it each time as there were problems when comms wasn't great.
				with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ServerSocket:

					# Connect to server and send data		
					ServerSocket.setblocking(False)					
					ServerSocket.sendto(bytes(SkipCountInfo, "utf-8"), (SERVER_HOST, SERVER_PORT))
				
			except:
				print ("Send Failure - who cares?  Not me.")
			

		print ("Exiting " + self.name)
		exit()

ServerMsgThread = ServerMessageThread(1, "Server Message Thread", 1) 
ServerMsgThread.start()
'''
