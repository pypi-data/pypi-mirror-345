



from woofs.Cloud_9.days_duration import calc_days_duration

def check_1 ():
	assert (
		calc_days_duration ('2024-07-23', '2024-07-24') ==
		2
	), calc_days_duration ('2024-07-23', '2024-07-24');
	
	assert (
		calc_days_duration ('2024-07-23', '2024-07-26') ==
		4
	), calc_days_duration ('2024-07-23', '2024-07-26');


checks = {
	"check 1": check_1
}


