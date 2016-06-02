
```python
from Vanilla import Van, Realized
import basic_pricer
import matplotlib.pyplot as plt
import simulator
import numpy as np
```

```python

''' simulate for different deltas and see distribution of returns assuming all 
 hedging happens at the same vol it is simulated (so expected value should be zero)
 prices are simulated under BS assumptions (normal returns) '''

spot = 1.00
vol = 0.15
hedge_vol = 0.15
expiry = 1/365
notional = 1000000.00
hedge_day = 144
num_sims = 30000

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
lower delta options will have wider distributions, but all of them will be centered around the realized vol, which is also the hedge vol. 

![image of dist by delta](https://cloud.githubusercontent.com/assets/14933405/15734135/55c59058-285a-11e6-8e16-d6a7077910db.png)

```python
if True:
    strike = spot
    call1 = Van(spot, strike, vol, expiry)
    hv = 0.10
    hvs = []
    bevols = []
    while hv < 0.21:
        print(hv)
        res = np.array(call1.sim_vol(simulator.rand_sim,num_sims, hedge_day, hv))
        print('mean: %8.4f ' %(np.mean(res)))
        print('stdev: %7.4f '%(np.std(res)))
        hvs.append(hv)
        bevols.append(np.std(res))
        label1 = 'hvol:%3.1f%%  mean:%4.2f  std:%4.2f'%(hv*100, np.mean(res),np.std(res))
        hv += 0.05
        plt.hist(res,bins=60,normed=1,alpha=0.5,label=label1)
    #plt.plot(hvs,bevols)
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)
    plt.show()
 ```
again as expected no matter what hedge vol we used the expected breakeven vol will always be the realized vol, and as expected the returns with the lowest variance are attained when using the actual realized vol to delta hedge.
what I find a bit surprising is the skew of the returns, when using a lower vol (which will result in more delta hedging) has a skew to the right, as in most of the time b.e. vol will be lower than avg. opposite when using a higher vol.
important to realize that only thing you can do is change the shape of returns, expected returns cannot be changed by hedging strategy.
and for lower delta options then the skew is even more pronunced
i believe the reason for the skew for higher hedge vols you hold more delta against strikes as you start getting pinned, so b.e. will be much lower 

returns for ATMF options
![image of dist by hedge vol](https://cloud.githubusercontent.com/assets/14933405/15734335/8a2ad43c-285c-11e6-8d5e-8655469a1d78.png)

returns for 25d options
![image of dist by hedge vol for 25d](https://cloud.githubusercontent.com/assets/14933405/15734611/8d34cd92-285f-11e6-864d-735f118f9a2a.png)
