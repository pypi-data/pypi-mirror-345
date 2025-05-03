

'''
	import woofs.clouds.Tradier.v1.markets.options.chains as options_chains
	options_chains.discover ({
		"symbol": "",
		"expiration": "",
		"authorization": ""
	})
'''

''''
	#
	#	Example: return options chain for expiration at index 0
	#	
	#
	#
	import woofs.clouds.Tradier.v1.markets.options.expirations as options_expirations
	import woofs.clouds.Tradier.v1.markets.options.chains as options_chains
	
	symbol = "BYND"
	
	expirations = options_expirations.discover ({
		"symbol": symbol,
		"authorization": ""
	});
	
	option_chain = options_chains.discover ({
		"symbol": symbol,
		"expiration": expiration,
		"parse_format": "0",
		
		"authorization": "",
	});
"'''

import woofs.clouds.Tradier.v1.markets.options.chains.parse_1 as parse_1
import requests
import json
import traceback

import rich

def discover (params):
	symbol = params ["symbol"]
	expiration = params ["expiration"]
	authorization = params ["authorization"]
	
	if ("parse_format" in params):
		parse_format = params ["parse_format"]
	else:
		parse_format = "1"
	
	response = requests.get (
		'https://api.tradier.com/v1/markets/options/chains',
		params = {
			'symbol': symbol, 
			'expiration': expiration, 
			'greeks': 'true'
		},
		headers = {
			'authorization': f'Bearer { authorization }', 
			'Accept': 'application/json'
		}
	)

	json_response = response.json ()
	options_available = json_response ["options"] ["option"];

	parsed = options_available;

	try:
		if (parse_format == "1"):
			parsed = parse_1.parse (
				symbol,
				options_available, 
				expiration
			)		
	
	except Exception as E:
		exception_traceback = traceback.format_exc()
	
		rich.print_json (
			data = {
				"parse exception": {
					"exception": str (E),
					"trace": exception_traceback.split ("\n"),
					"status code": response.status_code
				}
			}
		)
		
		raise Exception (E)

	return parsed