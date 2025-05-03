

'''
	Call Option Expensiveness:
	
		Eclecticism (Vernacular):
			Level Price = Strike Price
			Coin = Share
			
		Algorithms:
			coin_ask_price = "0.95" # USD
			
			#
			#	Distance, multiplicative, to winning 
			#	from the coin_ask_price.
			#
			#	Theory:
			#		Call option contracts are more relevant
			#		if the break_even is closer to the coin_ask_price.
			#
			distance = break_even / coin_ask_price
			
			#
			#	
			#	Weight based on 
			#		coin_ask_price distance from strike_price
			#
			#	Theory:
			#		
			#	
			#
			coin_distance = 1 / (abs (coin_ask_price - strike_price))
			
			aggregate_call_option_expensiveness = (
				summation (distance * coin_distance) /
				summation (coin_distance)
			)
'''

'''
	Notes:
		* 	This doesn't take into account the amount
			of contracts in play. (open_interest)
'''

'''
	symbol = "ETHA"

	from woofs.clouds.Tradier.v1.markets.quotes import ask_for_quote
	quote = ask_for_quote ({
		"symbol": symbol,
		"authorization": os.environ ['Tradier_API_Key']
	});
	coin_ask_price = quote ["ask"]


	import woofs.clouds.Tradier.procedures.options.combine as combine_options 
	call_options = combine_options.presently ({
		"symbol": symbol,
		"authorization": os.environ ['Tradier_API_Key']
	});
	
	from woofs.shows.call_option_expensiveness import call_option_expensiveness
	expensiveness = call_option_expensiveness ({
		"coin_ask_price": coin_ask_price,
		"call_options": call_options
	})
	
	from woofs.shows.call_option_expensiveness.smooth import generate_smooth_line
	from woofs.shows.call_option_expensiveness.plot import plot_data_with_smooth_line

	smooth_dates, smooth_values, predict = generate_smooth_line (expensiveness);
	day_100_value = predict (100)
	print(f"Value at day 100: {day_100_value:.6f}")


	plt = plot_data_with_smooth_line (expensiveness, smooth_dates, smooth_values);
	plot_path = normpath (join (this_directory, 'smoothed_plot.png'));
	plt.savefig (plot_path, bbox_inches = 'tight')
	plt.close ()
'''

from fractions import Fraction

def call_option_expensiveness (packet):
	coin_ask_price = Fraction (packet ["coin_ask_price"]);
	call_options = packet ["call_options"]
	
	
	expensiveness_at_expiration = []
	for expiration_line in call_options:
		expiration = expiration_line ["expiration"]		
		strikes = expiration_line ["calls"] ["strikes"]
		
		#print ("expiration:", expiration);
		
		numerator = 0
		denomenator = 0	
		for strike_line in strikes:
			try:
				#print ("strike_price:", strike_line ["strike"])
				
				strike_price = Fraction (strike_line ["strike"])
				ask_price = Fraction (strike_line ["prices"] ["ask"])
				break_even = ask_price + strike_price;
				
				distance = break_even / coin_ask_price;
				
				coin_distance = 1 / (abs (coin_ask_price - strike_price));
					
				numerator += (distance * coin_distance);
				denomenator += coin_distance;
			except Exception as E:
				print ("exception in call option expensiveness:", E)
		
		if (denomenator > 0):
			expensiveness_at_expiration.append (
				[ expiration, float (numerator / denomenator) ]
			);
		else:
			expensiveness_at_expiration.append (
				[ expiration, "" ]
			);

	return expensiveness_at_expiration;