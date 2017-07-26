# Thread to handle Rumbling on command.
class RumbleThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	
		
	def run(self):
		print ("Starting " + self.name)
		#print_time(self.name, self.counter, 5)
		
		# Some initialisation
		# LastDisplayTime = time.time()

		# print (SERVER_HOST, SERVER_PORT)

		while(1):
			# Do the Rumble as required by the Queue 
			if (RumbleQ.empty() == False):
				RumbleStr = RumbleQ.get_nowait()
				
				# Accept XML string that specifies rumble information 
				# <Rumble><Vib0Str>0-100</Vib0Str><Vib1Str>0-100</Vib1Str><Vib2Str>0-100</Vib2Str><MsDuration>0-10000</MsDuration></Rumble>  

				print (RumbleStr)
				RumbleElement = ElementTree.fromstring(RumbleStr)
		
				# If Rumble - process it. 
				VibeStr =[0,0,0]
				
				if (RumbleElement.tag == 'Rumble'):
					
					# Read through all the information
					for Child in RumbleElement:
						
						# Get Vib Array Strengths
						if (Child.tag == 'Vib0Str'):
							#print(Child.text)
							VibeStr[0] = int(Child.text)
							
						# Get Vib Array Strengths
						if (Child.tag == 'Vib1Str'):
							#print(Child.text)
							VibeStr[1] = int(Child.text)
							
						# Get Vib Array Strengths
						if (Child.tag == 'Vib2Str'):
							#print(Child.text)
							VibeStr[2] = int(Child.text)

						# Get the duration to rumble. 
						if (Child.tag == 'MsDuration'):
							#print(Child.text)
							msduration = int(Child.text)

					# Run the requested Vibrations
					
					for i in range(0,3):
						PWM = int(int(VibeStr[i])*255/100)
						if (PWM > 255):
							PWM =255 
							
						#print ("***", PWM)
						pi.set_PWM_dutycycle(Vibrators[i], PWM)
						
						#pi.set_PWM_dutycycle(Vibrators[i], 100)
					
					time.sleep(float(msduration/1000))
					#time.sleep(.05)
					for i in range(0,3):
						pi.set_PWM_dutycycle(Vibrators[i], 0)
					time.sleep(.3)
					
		print ("Exiting " + self.name)
		exit()
