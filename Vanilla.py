import basic_pricer as bp
import backtest
import matplotlib.pyplot as plt
from math import *

class Van(object):
    'BS Vanilla option pricing'

    def __init__(self, spot, strike, vol, expiry, is_call=True, ir_d=0.0,
                 ir_f=0.0, is_prem_for=False):
        self.spot = spot
        self.strike = strike
        self.vol = vol
        self.expiry = expiry
        self.is_call = is_call
        self.ir_d = ir_d
        self.ir_f = ir_f
        self.is_prem_for = is_prem_for
        self.fwd = spot * bp.df(ir_d,expiry) / bp.df(ir_f,expiry)

    def bs_price(self):
        return bp.bs_price(self.spot, self.strike, self.vol, self.expiry,
                           self.is_call, self.ir_d, self.ir_f, self.is_prem_for)

    def bs_price_vol(self, vol):
        return bp.bs_price(self.spot, self.strike, vol, self.expiry,
                           self.is_call, self.ir_d, self.ir_f, self.is_prem_for)

    def bs_call(self):
        return bp.bs_call(self.spot, self.strike, self.vol, self.expiry,
                          self.ir_d, self.ir_f, self.is_prem_for)
    
    def bs_put(self):
        return bp.bs_put(self.spot, self.strike, self.vol, self.expiry,
                         self.ir_d, self.ir_f, self.is_prem_for)

    def delta(self, is_call = True):
        return abs(bp.bs_delta(self.spot, self.strike, self.vol, self.expiry,
                               is_call, self.ir_d, self.ir_f))
    
    def imp_vol(self, price):
        return bp.implied_vol_bs(price, self.spot, self.strike, self.expiry,
                                 self.is_call, self.ir_d, self.ir_f,
                                 self.is_prem_for)

    def be_vol(self, spot_series, hedge_vol):
        return backtest.breakeven_vol(spot_series, self.strike, hedge_vol,
                                      self.expiry, self.ir_d, self.ir_f)

    def realized_pl(self, spot_series, notional, hedge_vol):
        return backtest.realized_pl(spot_series, notional, self.strike,
                                    self.vol, self.expiry, self.ir_d,
                                    self.ir_f, hedge_vol, self.is_call)
        
    def sim_vol(self, sim_func, num_sims, num_steps_day, hedge_vol):
        '''runs multiple simulators thru sim_func and returns array of
        all be_vols for this particular option
        '''
        bevols =[]
        for i in range(0,num_sims):
            prices = sim_func(self.spot, self.vol, self.expiry, 0.00,
                              int(num_steps_day*self.expiry*365))
            bevols.append(self.be_vol(prices, hedge_vol)*100)
        return bevols
    
    def sim_pl(self, sim_func, num_sims, num_steps_day, notional, hedge_vol):
        '''runs multiple simulators thru sim_func and returns array of
        all realized p/l for this particular option
        '''
        real_pl =[]
        for i in range(0,num_sims):
            prices = sim_func(self.spot, self.vol, self.expiry, 0.00,
                              int(num_steps_day*self.expiry*365))
            real_pl.append(self.realized_pl(prices, notional, hedge_vol))
        return real_pl
    
    def __str__(self):
        a = 'strike: %7.4f --  spot: %7.4f' \
            %(self.strike, self.spot)
        b = 'expiry: %7.4f --  vol: %7.2f%%' \
            %(self.expiry, self.vol*100)
        c = 'dom IR: %6.2f%% --  for IR: %4.2f%%' \
            %(self.ir_d*100, self.ir_f*100)
        d = 'fwd:    %7.4f' \
            %(self.fwd)
        e = '%4.1fD CALL --> premium: %6.2f bps' \
            %(self.delta(True)*100, self.bs_call()*10000)
        f = '%4.1fD PUT  --> premium: %6.2f bps' \
            %(self.delta(False)*100, self.bs_put()*10000)
        return (a +'\n'+ b +'\n' + c + '\n' + d + '\n' + e + '\n' + f)

class Realized(object):

    def __init__(self, spot_series, start, end, ir_d=0.0, ir_f=0.0):
        self.spot_series = spot_series
        self.start = start
        self.end = end
        self.ir_d = ir_d
        self.ir_f = ir_f

    def real_pl(self, notional, strike, vol, hedge_vol, is_call=True):
        return backtest.realized_pl(self.spot_series, notional, strike, vol,
                                    self.start - self.end, self.ir_d, self.ir_f,
                                    hedge_vol, is_call)

    def be_vol(self, strike, hedge_vol, is_call = True):
        return backtest.breakeven_vol(self.spot_series, strike, hedge_vol,
                                      self.start - self.end, self.ir_d,
                                      self.ir_f)

    def be_curve(self, low_k, high_k, hedge_vol, num_k=20, plots=True):
        curve_dict = {}
        inc = (high_k - low_k)/num_k
        for i in range(0,num_k+1):
            strike = low_k + inc*i
            temp = self.be_vol(strike, hedge_vol)
            curve_dict[strike] = temp*100
        if plots:
            plt.figure(1)
            plt.subplot(211)
            plt.scatter(list(curve_dict.keys()), list(curve_dict.values()))
            miny = min(list(curve_dict.values()))
            if miny < 0:
                miny = -abs(miny*1.1)
            else:
                miny = miny*0.9
            maxy = max(list(curve_dict.values()))*1.1
            plt.plot([self.spot_series[-1], self.spot_series[-1]], [miny, maxy],
                     'k-', linewidth=1.3)
            rv = self.real_vol()*100
            plt.plot([low_k, high_k], [rv, rv],'r--', linewidth=1.2)
            plt.axis([low_k, high_k, miny, maxy])
            plt.grid(True)
            plt.subplot(212)
            plt.plot(self.spot_series)
            plt.axis([0, len(self.spot_series), min(self.spot_series)*0.995,
                      max(self.spot_series)*1.005])
            plt.grid(True)
            plt.show()
        return curve_dict

    def be_curve_auto(self, hedge_vol, num_k=20, plots=True):
        ''' dont need to pass strike limits,
        auto calculated depending on vol and series
        '''
        expiry = self.start - self.end
        low_k = min(self.spot_series[0]*(1 - 2*hedge_vol*sqrt(expiry)),
                    min(self.spot_series)*0.99)
        high_k = max(self.spot_series[0]*(1 + 2*hedge_vol*sqrt(expiry)),
                     max(self.spot_series)*1.01)
        curve_dict = self.be_curve(low_k, high_k, hedge_vol, num_k, plots)
        return curve_dict

    def be_curve_mult_vol(self, low_k, high_k, hedge_vol, num_k=20):
        inc = (high_k - low_k)/num_k
        h_vols = [hedge_vol*0.9, hedge_vol, hedge_vol*1.1]
        vv = []
        for v in h_vols:
            strikes = []
            vols = []
            for i in range(0, num_k+1):
                strike = low_k + inc*i
                strikes.append(strike)
                temp = self.be_vol(strike, v)
                vols.append(100*temp)
            vv.append(vols)
        plt.figure(1)
        plt.subplot(211)
        miny = min(min(vv[0]), min(vv[1]), min(vv[2]))
        maxy = max(max(vv[0]), max(vv[1]), max(vv[2])) * 1.05
        if miny < 0:
            miny = -abs(miny*1.05)
        else:
            miny = miny*0.95
        plt.axis([low_k, high_k, miny, maxy])
        plt.plot([self.spot_series[-1], self.spot_series[-1]], [miny, maxy],
                 'k-', linewidth=1.3)
        rv = self.real_vol()*100
        plt.plot([low_k, high_k],[rv, rv],'k--', linewidth=1.5)
        label1 = 'vol down - %5.2f' %(h_vols[0]*100)
        label2 = 'hedge vol - %5.2f' %(h_vols[1]*100)
        label3 = 'vol up - %5.2f' %(h_vols[2]*100)
        plt.scatter(strikes, vv[0], c='blue', edgecolor='blue', alpha = 0.7,
                    label=label1)
        plt.scatter(strikes, vv[1], c='grey', edgecolor='grey', alpha = 0.7,
                    label=label2)
        plt.scatter(strikes, vv[2], c='red', edgecolor='red', alpha = 0.7,
                    label=label3)
        plt.axis([low_k, high_k, miny, maxy])
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3,
                   mode="expand", borderaxespad=0.)
        #plt.legend(bbox_to_anchor=(1.005, 1), loc=2, borderaxespad=0.)
        plt.grid(True)
        plt.subplot(212)
        plt.plot(self.spot_series)
        plt.axis([0, len(self.spot_series), min(self.spot_series)*0.995,
                  max(self.spot_series)*1.005])
        plt.grid(True)
        plt.show()
        return (strikes,vv)

    def real_vol(self):
        rv = bp.realized_vol(self.spot_series, self.start, self.end)
        return rv
