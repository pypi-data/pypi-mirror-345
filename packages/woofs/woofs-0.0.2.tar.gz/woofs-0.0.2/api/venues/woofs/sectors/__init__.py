

'''
	from woofs.sectors import sectors
	le_sectors = sectors ()
	
	internet_coins = le_sectors ["internet_coins"]
'''


def sectors ():

	internet_coins = [
		[ "ETHA", "Ethereum" ],
		[ "COIN", "Coinbase" ],
		[ "MSTR", "Micro Strategy" ],
	]
	
	exchanges = [
		[ "COIN", "Coinbase" ],
		[ "HOOD", "Robinhood" ],
		
	]
	
	coin_sports = [
		[ "FLUT", "Flutter Entertainment" ],
		[ "DKNG", "DraftKings Inc."],
		[ "LNW", "Light & Wonder"]		
	]
	
	bitcoin_mining = [
		
	]
	
	plant_based_afters = [
		[ "BYND", "Beyond Meat" ],
		[ "SOYB", "Soybeans" ]
	]
	
	materials = [
		[ "GLD", "Gold :: SPDR Gold Shares" ],
		[ "IAU", "Gold :: iShares Gold Trust" ],
		[ "SLX", "Steel :: VanEck Steel ETF" ],
		[ "WOOD", "Wood :: iShares Global Timber & Forestry ETF" ],
		[ "PALL", "Palladium :: Aberdeen Standard Physical Palladium Shares ETF" ],
		[ "PPLT", "Platinum :: Aberdeen Standard Physical Platinum Shares ETF" ],
		[ "REMX", "VanEck Rare Earth/Strategic Metals ETF" ]
	]
	
	ride_shops = [
		[ "AN", "AutoNation, Inc." ],
		[ "KMX", "CarMax, Inc." ],
		[ "CVNA", "Carvana Co." ],
		[ "LAD", "Lithia Motors, Inc." ]
	]
	
	thermies = [
		[ "FCEL", "" ]
	]
	
	#
	#	Real Estate
	#		Mortgages
	#
	#		Residential
	#		Commercial
	#
	#		Healthcare
	#
	#		Hotel + Motel
	#
	real_estate_mortgages = []
	real_estate__residential = [
		[ "USRT", "iShares Core U.S. REIT ETF" ]
	]
	
	#
	#	
	#	Star Heat Collection
	#
	#
	star_heat_collection = [
		[ "FSLR", "	First Solar, Inc." ],
		[ "NXT", "Nextracker Inc." ],
		[ "ENPH", "Enphase Energy, Inc." ],
		[ "RUN", "Sunrun Inc." ]
	]

	return {
		"business": [
			[ "IVV",  "iShares S&P 500" ],
			[ "USRT", "iShares Core US REIT ETF" ]
		],
		
		"coin_sports": coin_sports,
		
		"internet_coins": internet_coins,
		"materials": materials,
		
		"real_estate__residential": real_estate__residential,
		
		"ride_shops": ride_shops,
		"star_heat_collection": star_heat_collection
	}