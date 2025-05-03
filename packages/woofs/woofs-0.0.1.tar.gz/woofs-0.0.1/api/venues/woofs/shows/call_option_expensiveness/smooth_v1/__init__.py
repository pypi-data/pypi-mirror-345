
'''
	from woofs.shows.call_option_expensiveness.smooth import weighted_quadratic_fit
	weighted_quadratic_fit (data)
'''


import numpy as np
from datetime import datetime
from scipy.optimize import curve_fit

def weighted_quadratic_fit (data, weights=None):
	"""
	Perform weighted quadratic regression on date-value data.

	Parameters:
	- data: list of [date_str, value], e.g. [["2025-05-02", 1.03], ...]
	- weights: optional numpy array or list of weights for each point (default equal weights)

	Returns:
	- popt: optimized polynomial coefficients (a, b, c)
	- predict_func: a function that takes a date string and returns the fitted value
	"""
	# Convert date strings to ordinal numbers
	dates = np.array([datetime.strptime(d[0], "%Y-%m-%d").toordinal() for d in data])
	values = np.array([d[1] for d in data])
	
	# Normalize dates for numerical stability
	dates_norm = dates - dates[0]
	
	# Define quadratic polynomial model
	def poly2(x, a, b, c):
		return a * x**2 + b * x + c
	
	# If no weights provided, use equal weights
	if weights is None:
		weights = np.ones_like(values)
	else:
		weights = np.array(weights)
		if weights.shape != values.shape:
			raise ValueError("Weights must be the same shape as values")
	
	# Perform weighted curve fitting
	popt, pcov = curve_fit(poly2, dates_norm, values, sigma=1/weights, absolute_sigma=True)
	
	# Function to predict smoothed value for any date string within range
	def predict(date_str):
		date_ord = datetime.strptime(date_str, "%Y-%m-%d").toordinal()
		x = date_ord - dates[0]
		return poly2(x, *popt)
	
	return popt, predict

# Example usage:

'''
data = [
  ["2025-05-02", 1.0386270078353559],
  ["2025-05-09", 1.063285230929181],
  ["2025-05-16", 1.07392377325582],
  ["2025-05-23", 1.091270822906727],
  ["2025-05-30", 1.10040622189179],
  ["2025-06-06", 1.1153899800114775],
  ["2025-06-13", 1.1204187054134425],
  ["2025-06-20", 1.1208530232865173],
  ["2025-09-19", 1.1980538129633038],
]
'''