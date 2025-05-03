


'''

'''

import rich

def parse (
	integral_symbol,
	options_available, 
	expiration
):
	parsed = {
		"expiration": expiration,
		"calls": {
			"strikes": []
		},
		"puts": {
			"strikes": []
		}
	}
	
	'''
		 OPRA Feeds (Options) 
			A	NYSE Amex Options
			B	BOX Options Exchange
			C	Chicago Board Options Exchange (CBOE)
			H	ISE Gemini
			I	International Securities Exchange (ISE)
			M	MIAX Options Exchange
			N	NYSE Arca Options
			O	Options Price Reporting Authority (OPRA)
			P	MIAX PEARL
			Q	NASDAQ Options Market
			T	NASDAQ OMX BX
			W	C2 Options Exchange
			X	NASDAQ OMX PHLX
			Z	BATS Options Market
	'''
	'''
		MSFT:
			underlying: MSFT
			
			exch: Z
			
			
			
	'''
	for entry in options_available:	
		option_type = entry ["option_type"]
		
		the_exchange = entry ["exch"]
		the_bid_exchange = entry ["bidexch"]
		the_ask_exchange = entry ["askexch"]
		
		'''
		rich.print_json (data = {
			"the_bid_exchange": the_bid_exchange,
			"the_ask_exchange": the_ask_exchange,
			"the_exchange": the_exchange
		})
		'''
		
		#rich.print_json (data = entry)
		
		#assert (the_exchange == the_bid_exchange), [ the_exchange, the_bid_exchange ]
		assert (integral_symbol == entry ["underlying"]), [ integral_symbol, entry ["underlying"] ]
		assert (integral_symbol == entry ["root_symbol"]), [ integral_symbol, entry ["root_symbol"] ]
		
		
		data = {
			"strike": entry ["strike"],
			"description": entry ["description"],
			
			"prices": {
				"bid": entry ["bid"],
				"bid size": entry ["bidsize"],
				
				"ask": entry ["ask"],
				"ask size": entry ["asksize"],				
				
				"last": entry ["last"],
			},

			"contract size": entry ["contract_size"],
			"open interest": entry ["open_interest"],
		}
		
		if (option_type == "call"):
			parsed ["calls"] ["strikes"].append (data)
		
		
		elif (option_type == "put"):
			parsed ["puts"] ["strikes"].append (data)

	return parsed