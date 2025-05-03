
from woofs.shows.options.pricyness import options_pricyness
from woofs.shows.options.pricyness import show_the_results
from woofs.shows.options._physiques.physique_1.examples.BYND import ask_for_example

import json
from pprint import pprint

def check_1 ():
	options_physique_1 = options_pricyness ({
		"options physique 1": ask_for_example (),
		"share price": 6.15,
		"trade": "ask",
		"today": "2024-07-23"
	})
	
	show_the_results (options_physique_1)
	
	relevant = []
	for options_at_expiration in options_physique_1:
		expiration = options_at_expiration ["expiration"]
		
		try:
			days_until = options_at_expiration ["calculations"] ["days_until"]
		except Exception:
			days_until = "error"
		
		try:
			calls_to_puts_options_ask_pricyness = options_at_expiration ["calculations"] ["call:puts options ask pricyness ratio from zero"]
		except Exception as E:
			print ("Exception:", E)
			calls_to_puts_options_ask_pricyness = "error"
		
		relevant.append ({
			"dates_until": days_until,
			"calls_to_puts_options_ask_pricyness": calls_to_puts_options_ask_pricyness
		})
		
		#print (expiration, days_until, calls_to_puts_options_ask_pricyness)
		print (days_until, calls_to_puts_options_ask_pricyness)
		
	pprint (relevant, indent = 4)
	expected = [{   'calls_to_puts_options_ask_pricyness': -0.039164166885600205,
	        'dates_until': 3},
	    {   'calls_to_puts_options_ask_pricyness': -0.023152926820929176,
	        'dates_until': 10},
	    {   'calls_to_puts_options_ask_pricyness': 0.0817671283554322,
	        'dates_until': 17},
	    {   'calls_to_puts_options_ask_pricyness': -0.05950627620071747,
	        'dates_until': 24},
	    {   'calls_to_puts_options_ask_pricyness': 0.05344408709118609,
	        'dates_until': 31},
	    {   'calls_to_puts_options_ask_pricyness': 0.05506116464750965,
	        'dates_until': 38},
	    {   'calls_to_puts_options_ask_pricyness': -0.05443745179192239,
	        'dates_until': 59},
	    {   'calls_to_puts_options_ask_pricyness': -0.10619746057261503,
	        'dates_until': 115},
	    {   'calls_to_puts_options_ask_pricyness': -0.376385502501859,
	        'dates_until': 178},
	    {   'calls_to_puts_options_ask_pricyness': -0.14786628450829187,
	        'dates_until': 213},
	    {   'calls_to_puts_options_ask_pricyness': -0.476059530569793,
	        'dates_until': 514},
	    {   'calls_to_puts_options_ask_pricyness': -0.4624132588166794,
	        'dates_until': 542}]
	
	assert (
		json.dumps (relevant, sort_keys=True) == 
		json.dumps (expected, sort_keys=True)
	)
		
checks = {
	'check 1': check_1
}