

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

	print (ETHA)


	print ("check 1")
	

	


checks = {
	"check 1": check_1
}
