

'''
	from woofs.Cloud_9.add_days import Cloud_9_Add_Days
	Cloud_9_Add_Days ("2026-04-08", 182);
'''
'''
	from woofs.Cloud_9.add_days import Cloud_9_Add_Days
	from woofs.Cloud_9.here import Cloud_9_Here
	from woofs.Cloud_9.date_to_timestamp import Cloud_9_Seconds
	Cloud_9_Seconds (Cloud_9_Add_Days (Cloud_9_Here (), 182));
'''
from datetime import datetime, timedelta
import pytz

def Cloud_9_Add_Days (date_string, day_to_add):
	start_date = datetime.strptime (date_string, "%Y-%m-%d")
	new_date = start_date + timedelta (days = day_to_add)

	return new_date.strftime ("%Y-%m-%d")


