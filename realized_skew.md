realized b.e. vol skew using different vols
ran for 1 day option and 1yr option, since I am also simulating the price action is effectively the same just increasing the number of hedges per period
which means we would expect the 1 day options to have much more kinks (1yr option should be a lot smoother)

```python
from Vanilla import Van, Realized
import simulator
from math import *

spot = 1.0
vol = 0.15
hedge_vol = 0.15
expiry = 1/365
strike = 1.00
notional = 1.0
hedge_day = 144

prices = simulator.rand_sim(spot,vol,expiry, 0.00, int(365*expiry)*hedge_day)
low_strike = min(prices[0]*(1-1.0*hedge_vol*sqrt(expiry)),min(prices)*0.99)
high_strike = max(prices[0]*(1+1.0*hedge_vol*sqrt(expiry)),max(prices)*1.01)
day1 = Realized(prices,expiry,0.00)
dd = day1.be_curve_mult_vol(low_strike, high_strike, hedge_vol, 100)

```
1 year b.e. realized skew vol
![1y be skew vol](https://cloud.githubusercontent.com/assets/14933405/15734875/daa48156-2861-11e6-8fb7-884ba28d35ee.png)

1day b.e. realized skew vol (instance1 - pinned)
![1d be skew vola](https://cloud.githubusercontent.com/assets/14933405/15734872/d7125c70-2861-11e6-9b12-96c2b6a041a8.png)

1day b.e. realized skew vol (instance2 - negative vol)
![1d be skew volb](https://cloud.githubusercontent.com/assets/14933405/15734878/dd7a7912-2861-11e6-96d2-bfb7cd9b6ae5.png)
