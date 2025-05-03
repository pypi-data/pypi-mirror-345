


# woofs

## Install
```

```

## Relevant
```
https://etfdb.com/etfs/sector/#sector-power-rankings__return-leaderboard
```

## Call Option Expensiveness
```
from woofs.openings.call_option_opening import call_option_opening

Tradier_API_Key = os.environ ['Tradier_API_Key']

def coins__call_option_expensiveness (packet):
	coins = packet ["coins"]
	
	print ("call option day 100 expensiveness");
	for coin in coins:
		call_option = call_option_opening ({
			"Tradier_API_Key": Tradier_API_Key,
			"symbol": coin [0]
		});
		
		expensiveness = call_option ["call_option_expensiveness_day_100"];
		
		print (f"{ expensiveness } for { coin [0] } '{ coin [1] }'");


sectors = [
	[ "ETHA", "Ethereum" ],
	[ "IVV",  "iShares S&P 500" ],
	[ "USRT", "iShares Core US REIT ETF" ]
]

relevant = [
	[ "FSLR", "Solar" ]
]


coins__call_option_expensiveness ({
	"coins": relevant
});
```


## Call Option Expensiveness
### Show a Plot
```
import os
Tradier_API_Key = os.environ ['Tradier_API_Key']

from woofs.openings.call_option_opening import call_option_opening
call_option = call_option_opening ({
	"Tradier_API_Key": Tradier_API_Key,
	"symbol": "ETHA"
});

from woofs.shows.call_option_expensiveness.plot_2 import plot_call_option_expensiveness
plot_path = normpath (join (this_directory, 'smoothed_plot.png'));
plt = plot_call_option_expensiveness (
	call_option ["call_option_expensiveness"], 
	call_option ["call_option_expensiveness_smooth"]
);
plt.savefig (plot_path, bbox_inches = 'tight')
plt.close ()

```