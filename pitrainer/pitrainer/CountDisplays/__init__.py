# Thread to handle outputting to the OLED screen and sending to the server. 
# - to avoid spending too much time blocked on this.
class CountDisplayThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		#print_time(self.name, self.counter, 5)
		
		# Some initialisation
		LastDisplayTime = time.time()
		SkipCount = 0 

		print (SERVER_HOST, SERVER_PORT)

		while (1):
			# Print to the OLED Screen - Get the information from the Queue whenever available, but only update OLED screen once in a while
			# Screen is too slow for many updates. 
			if (q.empty() == False):
				SkipCount = q.get_nowait()
				
				SkipCountInfo = "<Skip><SkipCount>{:d}</SkipCount></Skip>" .format(SkipCount)
				
				try:
					# Open socket and send data - Open it each time as there were problems when comms wasn't great.
					with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ServerSocket:
						# Connect to server and send data		
						ServerSocket.setblocking(False)					
						ServerSocket.sendto(bytes(SkipCountInfo, "utf-8"), (SERVER_HOST, SERVER_PORT))
				except:
					print ("Send Failure - who cares?  Not me.")

			
			SkipCountStr = "{:d}".format(SkipCount)
			ElapsedTime = time.time() - LastDisplayTime
			
			if (ElapsedTime > 2):
				scrollphathd.clear()
				scrollphathd.write_string(SkipCountStr, x=0, y=0, font=font5x7, brightness=0.5)
				scrollphathd.show()
				LastDisplayTime = time.time()
				

		print ("Exiting " + self.name)
		exit()

SkipCountDisplayThread = CountDisplayThread(1, "Count Display Thread", 1) 
SkipCountDisplayThread.start()
