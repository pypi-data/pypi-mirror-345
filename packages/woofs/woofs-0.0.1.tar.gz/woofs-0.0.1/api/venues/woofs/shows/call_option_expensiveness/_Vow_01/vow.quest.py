
'''
[
	[
		"2025-05-02",
		1.0386270078353559
	],
	[
		"2025-05-09",
		1.063285230929181
	],
	[
		"2025-05-16",
		1.07392377325582
	],
	[
		"2025-05-23",
		1.091270822906727
	],
	[
		"2025-05-30",
		1.10040622189179
	],
	[
		"2025-06-06",
		1.1153899800114775
	],
	[
		"2025-06-13",
		1.1204187054134425
	],
	[
		"2025-06-20",
		1.1208530232865173
	],
	[
		"2025-09-19",
		1.1980538129633038
	],
	[
		"2025-12-19",
		1.2475867116582267
	]
]
'''

import rich

import json
import os
import pathlib

ETHA_path = str (os.path.normpath (os.path.join (
	pathlib.Path (__file__).parent.resolve (), 
	f"ETHA.options_combined.JSON"
)))

def check_1 ():
	with open (ETHA_path, 'r') as file:
		ETHA = json.load (file)

	ETHA_ask_price = 13.96

	from woofs.shows.call_option_expensiveness import call_option_expensiveness
	expensiveness = call_option_expensiveness ({
		"coin_ask_price": ETHA_ask_price,
		"call_options": ETHA
	});
	
	rich.print_json (data = expensiveness);
	
	assert (len (expensiveness) == 10)
	assert (expensiveness [0][1] == 1.0386270078353559, expensiveness [0][1])
	assert (expensiveness [1][1] == 1.063285230929181, expensiveness [1][1])
	assert (expensiveness [2][1] == 1.07392377325582, expensiveness [2][1])
	


checks = {
	"check 1": check_1
}
