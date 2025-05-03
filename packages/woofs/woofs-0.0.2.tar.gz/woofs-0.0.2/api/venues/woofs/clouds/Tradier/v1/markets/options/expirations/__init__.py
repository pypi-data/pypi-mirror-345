
'''
import woofs.clouds.Tradier.v1.markets.options.expirations as options_expirations
options_expirations.discover ({
	"symbol": "",
	"authorization": ""
})
'''

def discover (params):
	SYMBOL = params ["symbol"]
	AUTHORIZATION = params ["authorization"]

	PARSE_FORMAT = 1;

	import requests
	response = requests.get (
		'https://api.tradier.com/v1/markets/options/expirations',
		params = {
			'symbol': SYMBOL, 
			'includeAllRoots': 'true', 
			'strikes': 'false'
		},
		headers={
			'Authorization': f'Bearer { AUTHORIZATION }', 
			'Accept': 'application/json'
		}
	)
		
	return response.json ()['expirations']['date']
