

'''
	from woofs.shows.call_option_expensiveness.plot import plot_data_with_smooth_line
	plt = plot_data_with_smooth_line (expensiveness, smooth_dates, smooth_values);
	plot_path = normpath (join (this_directory, 'smoothed_plot.png'));
	plt.savefig (plot_path, bbox_inches = 'tight')
	plt.close ()
'''

import numpy as np
from datetime import datetime
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_data_with_smooth_line(data, smooth_dates, smooth_values):
	orig_dates = [datetime.strptime(d[0], "%Y-%m-%d") for d in data]
	orig_values = [d[1] for d in data]

	plt.figure (figsize=(10,6))

	# Plot original data points
	plt.scatter (orig_dates, orig_values, color='blue', label='Original Data')

	# Plot smooth curve
	plt.plot (smooth_dates, smooth_values, color='red', label='Smoothed Quadratic Fit')

	# Format the x-axis for dates
	plt.gca ().xaxis.set_major_locator(mdates.MonthLocator ())
	plt.gca ().xaxis.set_major_formatter(mdates.DateFormatter ('%Y-%m-%d'))
	plt.gcf ().autofmt_xdate ()  # Rotate date labels

	plt.title ('Original Data with Smoothed Weighted Quadratic Fit')
	plt.xlabel ('Date')
	plt.ylabel ('Value')
	plt.legend ()
	plt.grid (True)
	plt.tight_layout ()
	#plt.show()

	return plt;