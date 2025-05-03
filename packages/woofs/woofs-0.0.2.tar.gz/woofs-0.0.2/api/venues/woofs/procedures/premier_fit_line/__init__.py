
''''
from woofs.procedures.premier_fit_line import calculate_premier_fit_line
spots_with_fit = calculate_premier_fit_line ({
	"options_physique_1": options_physique_1
})
"'''

''''
{
	"days_until": "",
	"call:puts options ask pricyness ratio from zero": ""
}
"'''

import numpy as np
from scipy.stats import linregress

from pprint import pprint

def calculate_premier_fit_line (packet):
	options_physique_1 = packet ["options_physique_1"]

	spots = []
	for options_at_expiration in options_physique_1:
		expiration = options_at_expiration ["expiration"]
		
		try:
			days_until = options_at_expiration ["calculations"] ["days_until"]
		except Exception:
			days_until = "error"
		
		try:
			calls_to_puts_options_ask_pricyness = options_at_expiration [
				"calculations"
			] ["call:puts options ask pricyness ratio from zero"]
		except Exception:
			calls_to_puts_options_ask_pricyness = "error"
		
		#print (expiration, days_until, calls_to_puts_options_ask_pricyness)
		print (days_until, calls_to_puts_options_ask_pricyness)
		
		spots.append ({
			"days_until": days_until,
			"call:puts pricyness": calls_to_puts_options_ask_pricyness
		})
		
	# Extract X and Y data from the dictionary
	X = [entry['days_until'] for entry in spots]
	Y = [entry['call:puts pricyness'] for entry in spots]
	
	# Perform polynomial fit (linear fit in this case, degree=1)
	coefficients = np.polyfit(X, Y, 1)

	# Generate best-fit line
	best_fit_line = np.polyval(coefficients, X)
	
	
	def find_in_between ():
		orbit = 0;
		last_orbit = len (spots) - 1
		while (orbit <= last_orbit):
			spot_1 = spots [ orbit ]
			try:
				spot_2 = spots [ orbit + 1]
			except Exception:
				spot_2 = False
				
			if (spot_2 == False):
				return len (spots)
			
		return;
	
	#
	spots_with_fit = []
	#
	date_number = 0;
	date = 24
	#
	spot_number = 0;
	spot_number_last = len (spots) - 1;
	#
	while (date <= 700):
		print ('date:', date)
	
		this_date_added = False
		while (spot_number <= spot_number_last):
			print ('	check:', spots [ spot_number ] ["days_until"])
			#print ('	eq:', spots [ spot_number ] ["days_until"] == date)
			
			if (spots [ spot_number ] ["days_until"] <= date):
			
				#
				#	days_until = 
				#
				#
				if (spots [ spot_number ] ["days_until"] == date):
					spots_with_fit.append ({
						** spots [ spot_number ],
						"fit": float (np.polyval (coefficients, date)),
						#"eq": True
					})
					
					this_date_added = True
					
				else:
					spots_with_fit.append ({
						** spots [ spot_number ]
					})
			else:
				break;
				
			spot_number += 1
		
		if (this_date_added == False):
			spots_with_fit.append ({
				"days_until": date,
				"fit": float (np.polyval (coefficients, date))
			})
		
		date += 24;
	
	print ("spots_with_fit:", spots_with_fit)
	
	# np.polyval(coefficients, day)
	best_fit_value = np.polyval (coefficients, 365)
	
	print (best_fit_line, best_fit_value)
	pprint (spots)
	
	return spots_with_fit