
```python
from Vanilla import Van, Realized
import basic_pricer
import matplotlib.pyplot as plt
import simulator
import numpy as np
```
testing 

```python

''' simulate for different deltas and see distribution of returns assuming all 
 hedging happens at the same vol it is simulated (so expected value should be zero)
 prices are simulated under BS assumptions (normal returns) '''

spot = 1.00
vol = 0.12
hedge_vol = 0.12
expiry = 1/365
notional = 1000000.00
hedge_day = 144
num_sims = 10000

if True:
    i = 0.75
    stdev = []
    while i > 0.01:
        print(' ')
        print('delta k %6.4f'%(i))
        strike = basic_pricer.bs_strike(spot,i,vol,expiry)
        call1 = Van(spot,strike,vol,expiry)
        res = np.array(call1.sim_vol(simulator.rand_sim,num_sims, hedge_day, hedge_vol))
        ##res = np.array(call1.sim_pl(simulator.rand_sim,num_sims, hedge_day, notional, hedge_vol))
        print('mean: %8.4f ' %(np.mean(res)))
        print('stdev: %7.4f '%(np.std(res)))
        stdev.append(np.std(res))
        plt.hist(res,bins=100,normed=1.0,alpha=0.5)
        i -= 0.25
    plt.show()
```
![image of graph](C:/Users/Juan/Desktop/figure_1.png)
