
'''
	from woofs.shows.call_option_expensiveness.plot_2 import plot_call_option_expensiveness
	plot_call_option_expensiveness (
		call_option_expensiveness, 
		call_option_expensiveness_smooth
	);
	
	plot_path = normpath (join (this_directory, 'smoothed_plot.png'));
	plt.savefig (plot_path, bbox_inches = 'tight')
	plt.close ()
'''

import matplotlib.pyplot as plt
from datetime import datetime

def plot_call_option_expensiveness(dots_data, smooth_data):
	"""
	Plot call option expensiveness data points as dots and smooth data as a line.

	Args:
		dots_data (list): List of [date_str, value] pairs for the dots.
		smooth_data (list): List of [date_str, value] pairs for the smooth line.
	"""
	# Convert date strings to datetime objects and extract values
	dates_dots = [datetime.strptime(d[0], "%Y-%m-%d") for d in dots_data]
	values_dots = [d[1] for d in dots_data]

	dates_line = [datetime.strptime(d[0], "%Y-%m-%d") for d in smooth_data]
	values_line = [d[1] for d in smooth_data]

	# Create the plot
	plt.figure(figsize=(12, 6))

	# Plot dots and smooth line
	plt.plot(dates_dots, values_dots, 'o', label='Call Option Expensiveness')
	plt.plot(dates_line, values_line, '-', label='Call Option Expensiveness Smooth')

	# Customize plot
	plt.xlabel('Date')
	plt.ylabel('Expensiveness')
	plt.title('Call Option Expensiveness Over Time')
	plt.grid(True)
	plt.legend()
	plt.xticks(rotation=45)
	plt.tight_layout()

	# Show plot
	# plt.show()

	return plt


