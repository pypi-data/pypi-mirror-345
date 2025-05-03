

'''
	from woofs.Cloud_9.add_days import Cloud_9_Add_Days
	Cloud_9_Add_Days ("2026-04-08", 182);
'''

from woofs.Cloud_9.add_days import Cloud_9_Add_Days

def check_1 ():
	assert (Cloud_9_Add_Days ("2026-04-08", 1) == "2026-04-09");
	assert (Cloud_9_Add_Days ("2026-04-08", 182) == "2026-10-07");


checks = {
	"check 1": check_1
}


