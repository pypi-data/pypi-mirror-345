

'''
	from woofs.Cloud_9.date_to_timestamp import Cloud_9_Seconds
	Cloud_9_Seconds ("2026-04-08");
'''
def Cloud_9_Seconds (date_string):
	import datetime
	import pytz
	dt = datetime.datetime.strptime (date_string, "%Y-%m-%d")
	dt_utc = dt.replace (tzinfo = pytz.UTC)
	
	cloud_9_timestamp = int (dt_utc.timestamp ())
	
	return cloud_9_timestamp;