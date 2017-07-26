class UDPRecHandler(socketserver.BaseRequestHandler):
	
	
	"""
	The request handler class for our server.

	It is instantianted once per connection to the server, and must
	override the handle() method to implement communication to the
	client.
	
	"""

	def handle(self):
	
		print("handler")
		
		# self.request is the UDP socket connected to the client
		self.data = self.request[0].strip()
		socket = self.request[1]
		
	
		# Decode to ASCII so it can be processed.
		ClientStr = self.data.decode('ascii')
		
		# Put the data into an XML Element Tree
		try:
			print (ClientStr)
			ClientElement = ElementTree.fromstring(ClientStr)
	
			
			# If Attack received, then calcualte the effect on the opponent.
			
			if (ClientElement.tag == 'OpponentAttack'):

				print(ClientElement.text)
				
				PercentVibe = float(float(ClientElement.text)/16.0 *100) 
				print(PercentVibe)
				
				RumbleStr = "<Rumble><Vib0Str>{}</Vib0Str><Vib1Str>{}</Vib1Str><Vib2Str>{}</Vib2Str><MsDuration>{}</MsDuration></Rumble>" .format(int(PercentVibe), int(PercentVibe), int(PercentVibe), int(2 * PercentVibe))
				
				RumbleQ.put_nowait(RumbleStr)
				
				'''	
				# Read through all the information
				for Child in ClientElement:
					#print (Child.tag)
					
					# ZAccel does the damage - ignore if less than 2g
					if (Child.tag == 'ZAccel'):
						#print(Child.text)
						Damage = float(Child.text)

						
						if (Damage >2):
							Opponent.DecrementHealth(Damage)
							NumAttacks += 1
							#print (NumAttacks, HealthPoints)

							# Determine if Opponent is Defeated
							if (Opponent.CurrentHealth < 0):
								if (OpponentDefeated == False):
									FinalAttackNum = NumAttacks
									OpponentDefeated = True
									FightOver.set()
									
									# Player won, allow up to 50% regen
									Player.Regen(50)
									
									# Reward player with 2% of the opponents health points
									Player.RewardHealthPoint(0.02*Opponent.InitialHealth)
								
									# Keep Player Information up to date in XML as well. 
									PlayerMgr.UpdatePlayerXML(Player)
									PlayerMgr.UpdatePlayerFile()
	

									
								if (OpponentDefeated == True):
									print ("That dude is finished after - stop beating on him/her - Oh the Humanity", FinalAttackNum)

							
							# Send Opponent Information to the Client for display or other usage.
							self.SendOpponentInfo()
						
							# If first attack (player gets first punch), then start up the attacks from the opponent. 
							if (NumAttacks == 1):
								print ("run attacker thread")
								# Spin off opponent thread here.  
								AttackerThread = OpponentAttackThread(1, "Attacker Thread - Punch Up", 1, Opponent) 
								#AttackerThread.setDaemon(True)
								AttackerThread.start()
								FirstAttack = False
				'''
			else:
				print("Can't process string {}".format(ClientStr))
				
		except:
			print ("Trouble Processing String: {}" .format(ClientStr))
			raise()
			


# Class to handle the UDP Comms - manages the attacks and other messages from the Pi Fighter App, etc. 
class UDPRecThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter

	def run(self):
		print ("Starting " + self.name)
		
		try:
			#print ("UDP")
			hostname = socket.gethostbyname("KirbyPiZeroW")
			#hostname = "localhost"
			print(socket.getfqdn())
			print ("UDP - Trying again", hostname, int(config['UDP']['PI_TRAINER_PORT']))
			
			# Create the UDP server.  
			UDPserver = socketserver.UDPServer((hostname, int(config['UDP']['PI_TRAINER_PORT'])), UDPRecHandler)
	
			# Activate the server; this will keep running until you
			# interrupt the program with Ctrl-C
			UDPserver.serve_forever()
			
		except:
			print("UDP Exception")
			raise

			
		finally:
			UDPServer.close()
			exit()
