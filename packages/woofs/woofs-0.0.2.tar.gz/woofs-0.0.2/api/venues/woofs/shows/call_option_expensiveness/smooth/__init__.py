


'''
	from woofs.shows.call_option_expensiveness.smooth import generate_smooth_line
	smooth_dates, y_fit = generate_smooth_line ();
'''

'''
	Ask:
		return [
			[ date, value ],
			...
			[ date, value ]
		]
'''

import numpy as np
from datetime import datetime
from scipy.optimize import curve_fit

def generate_smooth_line(data, weights=None, num_points=200):
	"""
	Fit a weighted quadratic regression curve and generate smooth line points.
	Also returns a function to predict value at any day offset from start.

	Args:
		data (list): List of [date_str, value] pairs.
		weights (list or np.array, optional): Weights for each data point.
		num_points (int): Number of points to generate on the smooth curve.

	Returns:
		smooth_dates (list of datetime): Dates for the smooth curve.
		smooth_values (np.array): Corresponding smoothed values.
		predict_func (function): Function that takes day offset (int or float) and returns predicted value.
	"""
	# Convert date strings to ordinal numbers
	dates = np.array([datetime.strptime(d[0], "%Y-%m-%d").toordinal() for d in data])
	values = np.array([d[1] for d in data])
	dates_norm = dates - dates[0]

	# Quadratic polynomial model
	def poly2(x, a, b, c):
		return a * x**2 + b * x + c

	# Default equal weights if none provided
	if weights is None:
		weights = np.ones_like(values)
	else:
		weights = np.array(weights)
		if weights.shape != values.shape:
			raise ValueError("Weights must be the same shape as values")

	# Fit weighted quadratic curve
	popt, _ = curve_fit(poly2, dates_norm, values, sigma=1/weights, absolute_sigma=True)

	# Generate smooth x values and compute y values
	x_fit = np.linspace(dates_norm.min(), dates_norm.max(), num_points)
	y_fit = poly2(x_fit, *popt)

	# Convert back to datetime objects
	smooth_dates = [datetime.fromordinal(int(x + dates[0])) for x in x_fit]
	smooth_dates_2 = [datetime.fromordinal(int(x + dates[0])).strftime("%Y-%m-%d") for x in x_fit]

	#smooth_info = [[date, value] for date, value in zip(smooth_dates, y_fit)]
	smooth_info = [[date, float (value) ] for date, value in zip(smooth_dates_2, y_fit)]

	# Define prediction function for any day offset from start date
	def predict (day_offset):
		if day_offset > dates_norm.max ():
			return "Day offset is after the last expiration."
	
		try:
			amount = float (poly2 (day_offset, *popt))
			return f"{ amount:.6f}"
		except Exception as E:
			print ("expensiveness exception:", E);
		
		return "Day offset coud not be calculated."
	

	return smooth_dates, y_fit, predict, smooth_info