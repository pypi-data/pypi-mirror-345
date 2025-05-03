#/
#
import Emergency
#
#
import rich
#
#
import json
import pathlib
import pprint
from os.path import dirname, join, normpath
import os
import sys
import subprocess
import time
#
#\

this_directory = pathlib.Path (__file__).parent.resolve ()
monitors_path = str (normpath (join (this_directory, f"..")))
modules_path = str (normpath (join (this_directory, f"../..")))

promote = Emergency.on ({
	
	#	
	#	[necessary] 
	#	
	#	This is the file paths of the checks.
	#	
	"glob_string": monitors_path + '/**/*.quest.py',
	
	#
	#	[voluntary] 
	#		original = False
	#
	#	If False, the checks are run 
	#	one at a time.
	#
	"simultaneous": True,
	
	#
	#	[voluntary]
	#		original = 10
	#
	#	This is the limit on the amount
	#	of checks that can be run at the 
	#	same time.
	#
	"simultaneous_capacity": 50,

	#
	#	[voluntary]
	#		original = "99999999999999999999999"
	#
	#	After this time limit, lingering checks are stopped
	#	and reported as 
	#
	"time_limit": 60,
	
	#
	#	[voluntary]
	#		original = []
	#
	#	These are added to the sys.path of the process of
	#	each quest in the glob_string.
	#
	"module_paths": [
		modules_path
		# normpath (join (monitors_path, "stages"))
	],

	#
	#	[voluntary]
	#		original = False
	#			False returns the absolute path.
	#
	#	This is the path that is subtracted from the absolute path
	#	in the health report.
	#
	#	For example:
	#		absolute path: /habitats/venue.1/health/monitors/health_1.py
	#		relative path: /habitats/venue.1/health/monitors
	#		reported path: health_1.py
	#
	"relative_path": monitors_path,
	
	#
	#	[voluntary]
	#		original = False
	#			With False, a DB is not created 
	#			and reports aren't saved.
	#	
	#	This is where the results are kept.
	#	TinyDB is utilized.
	#
	"db_directory": normpath (join (this_directory, "DB")),
	
	#
	#	[voluntary]
	#		original = 1
	#
	#	This is how the "proceeds" (report) is presented.
	#	1 might not be as good as 2.
	#
	"aggregation_format": 2
})

promote ["off"] ()

#
#	This is a detailed report
#	of the technique.
#
rich.print_json (data = {
	"paths": promote ["proceeds"] ["paths"]
})

#
#	This is the checks that did 
#	not finish successfully.
#
rich.print_json (data = {
	"alarms": promote ["proceeds"] ["alarms"]
})

#
#	This is concise stats about
#	the  technique.
#
rich.print_json (data = {
	"stats": promote ["proceeds"] ["stats"]
})