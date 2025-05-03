

from woofs.Cloud_9.date_to_timestamp import Cloud_9_Seconds

def check_1 ():
	print ("check 1")
	
	assert (
		Cloud_9_Seconds ("2026-04-08") ==
		1775606400
	);


checks = {
	"check 1": check_1
}


