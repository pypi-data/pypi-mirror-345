


''''
	from woofs.clouds.Tradier.v1.markets.quotes import ask_for_quote
	quote = ask_for_quote ({
		"symbol": symbol,
		"authorization": Tradier_Private_Key
	})
	
	from woofs.shows.options.aggregate_optimism_level import Cloud_9_Seconds
	from woofs.shows.options.aggregate_optimism_level import G1__aggregate_optimism_accords_center_as_multiplier
	from woofs.shows.options.aggregate_optimism_level.plot_the_curve import estimate_fit_curve
	results = G1__aggregate_optimism_accords_center_as_multiplier (
		the_options_chains,
		coin_bid_price
	);
	
	plot = estimate_fit_curve (
		results,		
		symbol = symbol
	);
	
	plot.savefig ('plot.png')
	plot.close ()
"'''

'''
	
'''

import rich
from prettytable import PrettyTable
import numpy as np
import matplotlib.pyplot as plt

from woofs.Cloud_9.date_to_timestamp import Cloud_9_Seconds



def G1__aggregate_optimism_accords_center_as_multiplier__table (results):
	table = PrettyTable ()	
	table.field_names = [ 
		"expiration", 
		"expiration timestamp",
		"aggregate_optimism_level_for_expiration",
		"optimism multiplier", 
		"bid_size_sum" 
	]	
	for result in results:
		rich.print_json (data = result);
		# print (result ["expiration"], );
		
		table.add_row ([
			result ["expiration"],
			result ["expiration timestamp"],			
			result ["aggregate_optimism_level_for_expiration"],
			result ["optimism multiplier"],
			result ["bid_size_sum"]		
		])

	print (table.get_string ())

#
#
#	Optimism Accords (Calls):
#		1. Determine the aggregate center
#
#
def G1__aggregate_optimism_accords_center_as_multiplier (
	the_options_chains,
	coin_ask_price
):
	#
	#
	#	[ expiration, optimism_level, accords_accepted ]
	#
	#
	results = []

	''''
	expiration: 2027-01-15
		call: {'strike': 3.0, 'prices': {'bid': 1.0, 'ask': 1.05, 'last': 1.1}, 'contract size': 100, 'open interest': 5954}
		call: {'strike': 5.0, 'prices': {'bid': 0.62, 'ask': 1.0, 'last': 0.8}, 'contract size': 100, 'open interest': 1692}
		call: {'strike': 5.5, 'prices': {'bid': 0.35, 'ask': 3.65, 'last': None}, 'contract size': 100, 'open interest': 0}
		call: {'strike': 7.0, 'prices': {'bid': 0.26, 'ask': 0.74, 'last': 0.85}, 'contract size': 100, 'open interest': 490}
		call: {'strike': 10.0, 'prices': {'bid': 0.5, 'ask': 0.61, 'last': 0.5}, 'contract size': 100, 'open interest': 1309}
		call: {'strike': 12.0, 'prices': {'bid': 0.35, 'ask': 0.56, 'last': 0.4}, 'contract size': 100, 'open interest': 1553}
	"'''
	for expiration_grid in the_options_chains:
		expiration = expiration_grid ["expiration"]
		print ("expiration:", expiration);
		
		#
		#
		#	The calls for 1 expiration.
		#
		#
		calls = expiration_grid ["calls"] ["strikes"]
		
		accords_sum = 0;
		
		optimism_sum = 0;
		bid_size_sum = 0;
		
		for call in calls:
			print ("	call:", call);
				
			strike_price = call ["strike"];
			ask = call ["prices"] ["ask"];				
			bid_price = call ["prices"] ["bid"];				
				
			bid_size = call ["prices"] ["bid size"];				
			
			
			#
			#
			#	
			#
			#
			equality = strike_price + bid_price;			
	
	
			#
			#	Optimism perhaps shows 
			#		humbleness strike_price
			#		humbleness = optimism - ....
			#	
			#
			#	This is if the optimism strike_price of the accord
			#	is less than the price of the coin.
			#
			#	Therefore, this wouldn't be purchased
			#	unless a mistake occurred.
			#
			if (coin_ask_price >= equality):
				optimism_level = 0;
				
				#
				#
				#	Irrelevant
				#
				#
				
			else:
				optimism_level = equality * bid_size;
				bid_size_sum += bid_size;
				optimism_sum += optimism_level;

		
			rich.print_json (data = {
				"coin_ask_price": coin_ask_price,
				"strike_price": strike_price,
				"accord_bid_price": bid_price,
				"accord_bid_size": bid_size,
				"equality": equality,
				"optimism_level": optimism_level,
			});
			
			
		
		
		aggregate_optimism_level_for_expiration = 0
		optimism_multipli = 0
		if (bid_size_sum == 0):
			print ("no data");
		else:
			aggregate_optimism_level_for_expiration = optimism_sum / bid_size_sum;
			optimism_multipli = aggregate_optimism_level_for_expiration / coin_ask_price;
			
		results.append ({
			"expiration": expiration, 
			"expiration timestamp": Cloud_9_Seconds (expiration), 
			"optimism multiplier": "{:.3f}".format (round (optimism_multipli, 3)),
			"aggregate_optimism_level_for_expiration": "{:.3f}".format (round (aggregate_optimism_level_for_expiration, 3)),
			"bid_size_sum": bid_size_sum 
		})
		
		
	

	return results