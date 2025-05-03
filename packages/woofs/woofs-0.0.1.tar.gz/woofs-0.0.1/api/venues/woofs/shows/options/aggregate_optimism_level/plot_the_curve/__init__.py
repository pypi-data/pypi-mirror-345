


import numpy as np
import matplotlib.pyplot as plt

#
#
#	Weighted Regression Curve Fit:
#		Points prominence is based on bid_size_sum
#
#
def estimate_fit_curve (
	results,
	symbol = None,
	timestamp_to_search = None
):
	from scipy.optimize import curve_fit
	import matplotlib.dates as mdates
	import datetime

	expiration_timestamps = []
	optimism_multipliers = []
	bid_size_sums = []
	
	for result in results:
		expiration_timestamps.append (float (result ["expiration timestamp"]))
		optimism_multipliers.append (float (result ["optimism multiplier"]))
		bid_size_sums.append (float (result ["bid_size_sum"]))
		

	np_expiration_timestamps = np.array (expiration_timestamps)
	np_optimism_multipliers = np.array (optimism_multipliers)
	np_bid_size_sums = np.array (bid_size_sums)

	weights = np_bid_size_sums / np_bid_size_sums.max()

	#
	#
	#	Scatter plot with varying point sizes.
	#
	#
	plt.scatter (
		np_expiration_timestamps, 
		np_optimism_multipliers, 
		s = weights * 100
	);
	
	
	#def func (x, a, b):
	#	return a * x + b
	
	# Define a function for a parabola
	def func (x, a, b, c):
		return a * x**2 + b * x + c
	
	np_bid_size_sums = np.where (np_bid_size_sums == 0, 1e-9, np_bid_size_sums)
	#sigma = np.where (
	#	np_bid_size_sums > 0, 
	#	1 / np.sqrt (np_bid_size_sums),
	#	0
	#)
	
	#
	#
	#	https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
	#
	#
	popt, pcov = curve_fit (
		func, 
		np_expiration_timestamps, 
		np_optimism_multipliers, 
		
		sigma = 1 / np.sqrt (np_bid_size_sums)
	)
	
	#dates = [datetime.datetime.utcfromtimestamp(ts) for ts in np_expiration_timestamps]
	# print ("dates:", dates)
	
	plt.plot (
		np_expiration_timestamps, 
		func (np_expiration_timestamps, * popt), 
		color = 'black'
	)
	
	#date_formatter = mdates.DateFormatter('%y-%m-%d')
	#plt.gca().xaxis.set_major_formatter(date_formatter)

	# Rotate dates for better readability
	#plt.gcf().autofmt_xdate()

	'''
	plt.plot (
		np_expiration_timestamps, 
		p (np_expiration_timestamps), 
		color = 'red'
	);
	'''
	
	plt.xlabel ('Expiration Timestamp')
	plt.ylabel ('Optimism Multiplier')
	plt.title (f'{ symbol } Optimism Level')
	#plt.show()


	if timestamp_to_search is not None:
		optimism_multiplier_at_ts = func (timestamp_to_search, * popt)
		print (f"Optimism multiplier at timestamp { timestamp_to_search }: { optimism_multiplier_at_ts }")

	return [ plt ]
