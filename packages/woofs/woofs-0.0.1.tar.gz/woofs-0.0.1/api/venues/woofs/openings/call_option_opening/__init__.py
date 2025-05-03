
'''
	from woofs.openings.call_option_opening import call_option_opening
	call_option_opening ({
		"Tradier_API_Key": "",
		"symbol": "ETHA"
	});
'''

#
#
import os
#
#
from woofs.clouds.Tradier.v1.markets.quotes import ask_for_quote
import woofs.clouds.Tradier.procedures.options.combine as combine_options 
from woofs.shows.call_option_expensiveness import call_option_expensiveness
from woofs.shows.call_option_expensiveness.smooth import generate_smooth_line
from woofs.shows.call_option_expensiveness.plot import plot_data_with_smooth_line
#
#

def call_option_opening (packet):
	Tradier_API_Key = packet ["Tradier_API_Key"]
	symbol = packet ["symbol"]
	#symbol = "ETHA"
	
	quote = ask_for_quote ({
		"symbol": symbol,
		"authorization": Tradier_API_Key
	});
	coin_ask_price = quote ["ask"]

	
	call_options = combine_options.presently ({
		"symbol": symbol,
		"authorization": Tradier_API_Key
	});

	expensiveness = call_option_expensiveness ({
		"coin_ask_price": coin_ask_price,
		"call_options": call_options
	});
	
	smooth_dates, smooth_values, predict, smooth_info = generate_smooth_line (expensiveness);
	day_100_expensiveness = predict (100)
	
	return {
		"symbol": symbol,
		"coin_ask_price": coin_ask_price,
		"call_options": call_options,
		"call_option_expensiveness": expensiveness,
		"call_option_expensiveness_smooth": smooth_info,
		"call_option_expensiveness_day_100": day_100_expensiveness
	}
	
	