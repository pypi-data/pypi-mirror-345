




'''
	Call Option Expensiveness:
	
		Eclecticism (Vernacular):
			Level Price = Strike Price
			Coin = Share
			
		Algorithms:
			share_price = "0.95" # USD
			
			distance = break_even / share_price
			
			coin_distance = 1 / (abs (coin_price - level_price))
			
			aggregate_call_option_expensiveness = (
				summation (distance * coin_distance) /
				summation (coin_distance)
			)
			
			active_contracts = contract_size * open_interest
'''

'''
	Notes:
		* 	Take into account the amount
			of contracts in play. (open_interest * contract size)
'''

