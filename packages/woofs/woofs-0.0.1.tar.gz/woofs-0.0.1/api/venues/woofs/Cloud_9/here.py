

'''
	from woofs.Cloud_9.here import Cloud_9_Here
	Cloud_9_Here ();
'''

from datetime import datetime

def Cloud_9_Here ():
	today_date = datetime.today ().date ()
	formatted_date = today_date.strftime ('%Y-%m-%d')
	return formatted_date

