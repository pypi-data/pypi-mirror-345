
#	python3 emergency.proc.py "shows/options/pricyness/_sustain/2/sustain_2.py"

from woofs.shows.options.pricyness import options_pricyness
from woofs.shows.options.pricyness import show_the_results
from woofs.shows.options._physiques.physique_1.examples.BYND import ask_for_example

import json
from pprint import pprint

import pathlib
from os.path import dirname, join, normpath

this_directory = pathlib.Path (__file__).parent.resolve ()	

def save_options_to_FS (options_chains, symbol):
	file_path = str (normpath (join (this_directory, symbol + ".JSON")))
	with open(file_path, 'w') as json_file:
		json.dump(options_chains, json_file, indent=4)

def ask_FS_for_options (symbol):
	file_path = str (normpath (join (this_directory, symbol + ".JSON")))
	with open(file_path, 'r') as json_file:
		data = json.load(json_file)
		return data;

def check_1 ():
	spots = options_pricyness ({
		"options physique 1": ask_for_example (),
		"share price": 6.15,
		"trade": "ask",
		"today": "2024-07-23",
		
		"insert_fit_line": "yes"
	})
		
	pprint (spots, indent = 4)
	
	save_options_to_FS (spots, "BYND")
	
	spots_expected = ask_FS_for_options ("BYND")
		
	assert (
		json.dumps (spots, sort_keys=True) ==
		json.dumps (spots_expected, sort_keys=True)		
	)	
		
checks = {
	'check 1': check_1
}