




'''
	#
	#	https://documentation.tradier.com/brokerage-api/reference/exchanges
	#
	#	Q	NASDAQ OMX
	#	N	NYSE
	#
	#	P	NYSE Arca
	#	A	NYSE MKT
	#	
	import woofs.clouds.Tradier.v1.markets.lookup as lookup_symbol
	lookup_symbol.discover ({
		"symbol": "",
		"exchanges": "Q,N",
		"authorization": ""
	})
'''


import woofs.clouds.Tradier.v1.markets.options.chains.parse_1 as parse_1
import requests
import json
import traceback

import rich

def discover (params):
	symbol = params ["symbol"]
	exchanges = params ["exchanges"]
	
	authorization = params ["authorization"]
	
	parse_format = "1"
	
	response = requests.get (
		'https://api.tradier.com/v1/markets/lookup',
		params = {
			'q': symbol, 
			'exchanges': exchanges, 
			'greeks': 'true'
		},
		headers = {
			'authorization': f'Bearer { authorization }', 
			'Accept': 'application/json'
		}
	)

	json_response = response.json ()
	securities_list = json_response ["securities"] ["security"];


	for security in securities_list:
		if (security ["symbol"] == symbol):
			return security
	
	rich.print_json (data = securities_list)
	raise Exception ("not found")