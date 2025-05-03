



'''
	from woofs.shows.options._physiques._physique_1.assertions import assert_physique_1 
	assert_physique_1 (shape_1)
'''

def are_equal (v1, v2):
	try:
		assert (v1 == v2);
	except Exception as E:
		print ("not equal:", v1, v2)
		raise Exception (E)

	return;


def assert_physique_1 (shape_1):
	are_equal (type (shape_1), list)
	assert (len (shape_1) >= 1), len (shape_1)
	
	expirations = shape_1;
	
	for expiration in expirations:
		assert ("expiration" in expiration)

		assert ("calls" in expiration)
		assert ("strikes" in expiration ["calls"])
		assert (len (expiration ["calls"]["strikes"]) >= 1), len (expiration ["calls"]["strikes"])
	
		assert ("puts" in expiration)
		assert ("strikes" in expiration ["puts"])
		assert (len (expiration ["puts"]["strikes"]) >= 1), len (expiration ["puts"]["strikes"])

		call_strikes = expiration ["calls"]["strikes"]
		put_strikes = expiration ["puts"]["strikes"]
		
		for strike in call_strikes:
			assert ("strike" in strike)
			
			assert ("prices" in strike)
			assert ("bid" in strike ["prices"])
			assert ("ask" in strike ["prices"])
			assert ("last" in strike ["prices"])
			
			assert ("contract size" in strike)
			assert ("open interest" in strike)
		

		for strike in put_strikes:
			assert ("strike" in strike)
			
			assert ("prices" in strike)
			assert ("bid" in strike ["prices"])
			assert ("ask" in strike ["prices"])
			assert ("last" in strike ["prices"])
			
			assert ("contract size" in strike)
			assert ("open interest" in strike)
		
