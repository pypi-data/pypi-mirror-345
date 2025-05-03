
''''
from woofs.clouds.Tradier.v1.markets.quotes import ask_for_quote
quote = ask_for_quote ({
	"symbol": "",
	"authorization": ""
})

share_price_ask = quote ["ask"]
"'''

import requests
from pprint import pprint

def ask_for_quote (packet):
	authorization = packet ["authorization"]
	symbol = packet ["symbol"]

	response = requests.get('https://api.tradier.com/v1/markets/quotes',
		params = {
			'symbols': symbol,
			'greeks': 'false'
		},
		headers = {
			'Authorization': f'Bearer { authorization }', 
			'Accept': 'application/json'
		}
	)
	json_response = response.json()
	#print(response.status_code)
	#pprint (json_response)

	quote = json_response ['quotes'] ['quote']
	
	return quote;
