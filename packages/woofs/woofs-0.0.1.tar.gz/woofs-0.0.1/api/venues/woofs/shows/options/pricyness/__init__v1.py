


''''
	from woofs.shows.options.pricyness import options_pricyness
	options_pricyness ({
		"options physique 1": [],
		"vote price": 
		"trade": "ask"
	})
"'''

''''
	pricyness of asks
	pricyness of bids
"'''

''''
	level_price
		@ strike_price
		----
		
	cupcake_price
		@ share_price
		----
		@ vote price
		
	fair
		@ break_even
		----
		@ tie
		@ draw
"'''

import rich


''''
	{
		"distance": distance,
		"share_distance": share_distance
	}
	
	summation: distance * share_distance
	----
	summation: share_distance
"'''
def calculate_cohesive_share_distance (distances):
	numerator = 0
	denomenator = 0;
	
	for distance in distances:
		numerator += distance ["distance"] * distance ["share_distance"]
		denomenator += distance ["share_distance"]
		
	return numerator / denomenator;
		





''''


	level_trade_price = level_price + trade_price;

	vote_distance = 1 / (abs (vote_price) - strike_price)
"'''
def calculate_share_distance (share_price, strike_price):
	return 1 / abs (share_price - strike_price)




#
#	option_price_distance_from_share_price
#
#	example:
''''
	distance = break_even / share_price

	example:
		level	ask		break_even		distance
		0.50	0.60	1.10			1.157
		1.00	0.45	1.45			1.526

"'''
def calculate_distance (break_even, share_price):
	print ("distance:", f"{ break_even } / { share_price }")

	return break_even / share_price;

#
#	@ direction = put or call
#	@ trade = ask or bid
#
def calculate_break_even (strike_price, direction, trade_price):
	if (direction == "call"):
		return strike_price + trade_price
		
	return strike_price + trade_price



def calculate_ratio (number_1, number_2):
	if (number_1 == number_2):
		return "1:1"
	
	if (number_1 > number_2):
		return f"{ number_1 / number_2 }:1"

	if (number_1 < number_2):
		return f"1:{ number_2 / number_1 }"
		
	raise Exception ("Unaccounted for")


def options_pricyness (packet):
	options_physique_1 = packet ["options physique 1"]
	share_price = packet ["vote price"]
	trade = packet ["trade"]
	
	#
	#	orbit through the expirations
	#	
	#
	for options_at_expiration in options_physique_1:
		try:
	
			expiration = options_at_expiration ["expiration"]
			puts = options_at_expiration ["puts"]
			calls = options_at_expiration ["calls"]
			
			rich.print_json (data = {
				"puts": puts
			})
			
			
			#
			#	orbit through the calls
			#	
			#
			distances = []
			for level_details in calls ["strikes"]:
				strike_price = level_details ["strike"]
				trade_price = level_details ["prices"] [ trade ]
				
				#
				#	if open_interest == 0, skip
				#	
				#	signifies a fake ask price.
				#
				open_interest = level_details ["open interest"]
				if (open_interest == 0):
					continue;
				
				
				break_even = calculate_break_even (strike_price, "call", trade_price)
				distance = calculate_distance (break_even, share_price)
				share_distance = calculate_share_distance (share_price, strike_price)
				
				distances.append ({
					"distance": distance,
					"share_distance": share_distance
				})
				
				print ("call:", level_details)
				print ("distance:", distance)
				print ("share_distance:", share_distance)
				print ()
				
				if ("calculations" not in level_details):
					level_details ["calculations"] = {}
				
				level_details ["calculations"] ["distance"] = distance
				level_details ["calculations"] ["share_distance"] = share_distance
			
			cohesive_share_distance = calculate_cohesive_share_distance (distances)
			if ("calculations" not in calls):
				calls ["calculations"] = {}
				
			calls ["calculations"] ["cohesive_share_distance"] = cohesive_share_distance
			
			#
			#	orbit through the puts
			#	
			#
			distances = []
			for level_details in puts ["strikes"]:
				strike_price = level_details ["strike"]
				open_interest = level_details ["open interest"]
				
				trade_price = level_details ["prices"] [ trade ]
				
				#
				#	if open_interest == 0, skip
				#	
				#	signifies a fake ask price.
				#
				open_interest = level_details ["open interest"]
				if (open_interest == 0):
					continue;
				
				break_even = calculate_break_even (strike_price, "put", trade_price)
				distance = calculate_distance (break_even, share_price)
				share_distance = calculate_share_distance (share_price, strike_price)
				
				distances.append ({
					"distance": distance,
					"share_distance": share_distance
				})
				
				print ("put:", level_details)
				print ("distance:", distance)
				print ("share_distance:", share_distance)

				print ()
				
				if ("calculations" not in level_details):
					level_details ["calculations"] = {}
				
				level_details ["calculations"] ["distance"] = distance
				level_details ["calculations"] ["share_distance"] = share_distance
				
				
				
			cohesive_share_distance = calculate_cohesive_share_distance (distances)
			if ("calculations" not in puts):
				puts ["calculations"] = {}
				
			puts ["calculations"] ["cohesive_share_distance"] = cohesive_share_distance
		
			#
			#	expiration level calculations
			#
			#
			if ("calculations" not in options_at_expiration):
				options_at_expiration ["calculations"] = {}
			
			options_at_expiration ["calculations"] ["call:puts options ask pricyness"] = calculate_ratio (
				calls ["calculations"] ["cohesive_share_distance"],
				puts ["calculations"] ["cohesive_share_distance"]
			)
		
		except Exception as E:
			print ("Exception:", E)
		
	rich.print_json (data = {
		"options_physique_1": options_physique_1
	})
	
	for options_at_expiration in options_physique_1:
		expiration = options_at_expiration ["expiration"]
		
		try:
			calls_to_puts_options_ask_pricyness = options_at_expiration ["calculations"] ["call:puts options ask pricyness"]
		except Exception:
			calls_to_puts_options_ask_pricyness = "error"
		
		print (expiration, calls_to_puts_options_ask_pricyness)
		
		
		
	
	return;