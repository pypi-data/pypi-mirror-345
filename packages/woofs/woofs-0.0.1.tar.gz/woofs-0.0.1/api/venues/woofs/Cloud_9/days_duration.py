
''''
from woofs.Cloud_9.days_duration import calc_days_duration
calc_days_duration ('2024-07-23', '2026-07-23')
"'''

from datetime import datetime


def calc_days_duration (date_1_string, date_2_string):
	date_1 = datetime.strptime (date_1_string, '%Y-%m-%d')
	date_2 = datetime.strptime (date_2_string, '%Y-%m-%d')
	difference = date_2 - date_1
	days_duration = difference.days
	
	return days_duration + 1;


