from Vanilla import Van, Realized
import basic_pricer
import matplotlib.pyplot as plt
import simulator
import numpy as np

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

if False:
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
        label1 = 'k:%3.0fd mean:%4.2f  std:%4.2f'%(i*100, np.mean(res),np.std(res))
        plt.hist(res,bins=80,normed=1.0,alpha=0.5,label=label1)
        i -= 0.25
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)
    plt.show()

''' now I want to simulate different hedgevol '''

if True:
    strike = basic_pricer.bs_strike(spot,0.25,vol,expiry)
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

