

import woofs.clouds.Tradier.procedures.options.combine as combine_options  
from woofs.shows.options._physiques.physique_1.assertions import assert_physique_1 
from woofs._essence import retrieve_essence
	

def check_1 ():
	essence = retrieve_essence ()
	Tradier_Private_Key = essence ["clouds"] ["Tradier"] ["private_key"]
	
	print ("essence:", essence)

	options_chains = combine_options.presently ({
		"symbol": "VTI",
		"authorization": Tradier_Private_Key
	})	
	
	assert_physique_1 (options_chains)
	
	
	#print ("options_chains:", options_chains)

	return;
	
	
checks = {
	'structure of the Tradier options': check_1
}