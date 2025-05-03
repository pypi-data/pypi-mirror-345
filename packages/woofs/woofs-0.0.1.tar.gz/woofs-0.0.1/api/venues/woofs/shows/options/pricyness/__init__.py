


''''
	from woofs.shows.options.pricyness import options_pricyness
	options_pricyness ({
		"options physique 1": [],
		"vote price": 
		"trade": "ask",
		"today": "2024-07-23",
		
		"insert_fit_line": "yes"
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
from pprint import pprint

from woofs.procedures.spacedate.days_between import calc_days_between
from woofs.procedures.premier_fit_line import calculate_premier_fit_line


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
	#print ("distance:", f"{ break_even } / { share_price }")
	return break_even / share_price;

#
#	@ direction = put or call
#	@ trade = ask or bid
#
def calculate_break_even (strike_price, direction, trade_price):
	if (direction == "call"):
		return strike_price + trade_price
		
	return strike_price + trade_price

def calculate_ratio_from_zero (number_1, number_2):
	if (number_1 == number_2):
		return 0
	
	if (number_1 > number_2):
		return (number_1 / number_2) - 1
		
	if (number_1 < number_2):
		return -(number_2 / number_1) + 1
		
	raise Exception ("Unaccounted for")

def calculate_ratio_v1 (number_1, number_2):
	if (number_1 == number_2):
		return [ 1, 1 ]
	
	if (number_1 > number_2):
		return [ number_1 / number_2, 1 ]
		
	if (number_1 < number_2):
		return [ 1, number_2 / number_1 ]
		
	raise Exception ("Unaccounted for")


def show_the_results (options_physique_1):
	for options_at_expiration in options_physique_1:
		expiration = options_at_expiration ["expiration"]
		
		try:
			days_until = options_at_expiration ["calculations"] ["days_until"]
		except Exception:
			days_until = "error"
		
		try:
			calls_to_puts_options_ask_pricyness = options_at_expiration ["calculations"] ["call:puts options ask pricyness ratio from zero"]
		except Exception as E:
			print ("Exception:", E)
			calls_to_puts_options_ask_pricyness = "error"
		
		#print (expiration, days_until, calls_to_puts_options_ask_pricyness)
		print (days_until, calls_to_puts_options_ask_pricyness)

def options_pricyness (packet):
	options_physique_1 = packet ["options physique 1"]
	share_price = packet ["share price"]
	trade = packet ["trade"]
	today = packet ["today"]
	
	if ("insert_fit_line" in packet):
		insert_fit_line = packet ["insert_fit_line"]
	else:
		insert_fit_line = "no"
	
	#
	#	orbit through the expirations
	#	
	#
	for options_at_expiration in options_physique_1:
		try:
			expiration = options_at_expiration ["expiration"]
			days_until = calc_days_between (today, expiration)
			
			if ("calculations" not in options_at_expiration):
				options_at_expiration ["calculations"] = {}
			
			options_at_expiration ["calculations"] ["days_until"] = days_until
			
			
			puts = options_at_expiration ["puts"]
			calls = options_at_expiration ["calls"]
			
			#rich.print_json (data = {
			#	"puts": puts
			#})
			
			
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
				
				#print ("call:", level_details)
				#print ("distance:", distance)
				#print ("share_distance:", share_distance)
				##print ()
				
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
				
				#print ("put:", level_details)
				#print ("distance:", distance)
				#print ("share_distance:", share_distance)
				#print ()
				
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
			options_at_expiration ["calculations"] ["call:puts options ask pricyness ratio from zero"] = calculate_ratio_from_zero (
				calls ["calculations"] ["cohesive_share_distance"],
				puts ["calculations"] ["cohesive_share_distance"]
			)
			
			options_at_expiration ["calculations"] ["call:puts options ask pricyness ratio"] = calculate_ratio_v1 (
				calls ["calculations"] ["cohesive_share_distance"],
				puts ["calculations"] ["cohesive_share_distance"]
			)
		
		except Exception as E:
			print ("Exception:", E)
	
	
	if (insert_fit_line == "yes"):
		return calculate_premier_fit_line ({
			"options_physique_1": options_physique_1
		})
		
		
		
	return options_physique_1