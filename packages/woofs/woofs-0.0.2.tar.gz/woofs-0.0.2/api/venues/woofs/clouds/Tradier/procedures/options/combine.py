
'''
	import woofs.clouds.Tradier.procedures.options.combine as combine_options  
	call_options = combine_options.presently ({
		"symbol": symbol,
		"authorization": authorization,
		"puts": "nah"
	})
'''

'''
	returns:
	[
		{
			"expiration": "",
			"calls": {
				"strikes": [
					{
						"strike": 0.5,
						"prices": {
							"bid": 1.61,
							"ask": 4.5,
							"last": 2.31
						},
						"contract size": 100,
						"open interest": 19
					}
				]
			},
			"puts": {
				
			}
		},
		{
			"expiration": "",
		}
	]
'''


import woofs.clouds.Tradier.v1.markets.options.expirations as options_expirations
import woofs.clouds.Tradier.v1.markets.options.chains as options_chains

from woofs.shows.options._physiques.physique_1.assertions import assert_physique_1 



from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
def parallel (
	the_move,
	parameters
):
	proceeds = []
	
	with ThreadPoolExecutor () as executor:
		the_chains = executor.map (
			the_move, 
			parameters
		)
		executor.shutdown (wait = True)

		for chain in the_chains:
			proceeds.append (chain)
		
	return proceeds

def presently (parameters):
	symbol = parameters ["symbol"]
	authorization = parameters ["authorization"]
	
	if ("puts" in parameters):
		puts = parameters ["puts"]
	else:
		puts = "nah"

	#
	#	This gets the options 
	#	expirations list.
	#
	expirations = options_expirations.discover ({
		"symbol": symbol,
		"authorization": authorization
	})
	
	#
	#	This retrieves the info about
	#	the option at the sent expiration.
	#
	def retrieve_options_chains (expiration):
		the_chain =  options_chains.discover ({
			"symbol": symbol,
			"expiration": expiration,
			"authorization": authorization
		})
				
		return the_chain;

	proceeds = parallel (
		the_move = retrieve_options_chains,
		parameters = expirations
	)

	assert_physique_1 (proceeds)

	if (puts != "yah"):
		for proceed in proceeds:
			del proceed ["puts"]


	return proceeds