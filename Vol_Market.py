import basic_pricer as bp
import numpy as np
from math import *
import Event_Gap
import matplotlib.pyplot as plt

class Skew(object):

    def __init__(self, spot, expiry, ir_d, ir_f, atm_vol, rr_25, rr_10,
                 fly_25, fly_10):
        self.spot = spot
        self.fwd = spot * bp.df(ir_d,expiry) / bp.df(ir_f,expiry)
        self.expiry = expiry
        self.ir_d = ir_d
        self.ir_f = ir_f
        self.atm_vol = atm_vol
        self.rr_25 = rr_25
        self.rr_10 = rr_10
        self.fly_25 = fly_25
        self.fly_10 = fly_10
        self.call_25 = atm_vol + fly_25 + rr_25/2.0
        self.put_25 = atm_vol + fly_25 - rr_25/2.0
        self.call_10 = atm_vol + fly_10 + rr_10/2.0
        self.put_10 = atm_vol + fly_10 - rr_10/2.0
        self.call_25_k = bp.bs_strike(spot, 0.25, self.call_25, expiry, True,
                                      ir_d, ir_f)
        self.call_10_k = bp.bs_strike(spot, 0.10, self.call_10, expiry, True,
                                      ir_d, ir_f)
        self.put_25_k = bp.bs_strike(spot, 0.25, self.put_25, expiry, False,
                                     ir_d, ir_f)
        self.put_10_k = bp.bs_strike(spot, 0.10, self.put_10, expiry, False,
                                     ir_d, ir_f)
        self.fitted = self.fit_skew()

    def fit_skew(self):
        ''' this needs improvement, too simplistic, can't even match
        datapoint don't want to have higher poly, prob need some splines
        or something '''

        vols = [self.put_10, self.put_25, self.atm_vol, self.call_25,
                self.call_10]
        strikes = [self.put_10_k, self.put_25_k, self.fwd, self.call_25_k,
                   self.call_10_k]
        coeff = np.polyfit(strikes, vols, 2)
        self.beta_0 = coeff[2]
        self.beta_1 = coeff[1]
        self.beta_2 = coeff[0]
        self.call25k_act = self.get_strike(0.25, True)
        self.call10k_act = self.get_strike(0.10, True)
        self.put25k_act = self.get_strike(0.25, False)
        self.put10k_act = self.get_strike(0.10, False)
        self.call25v_act = self.get_vol(self.call25k_act)
        self.call10v_act = self.get_vol(self.call10k_act)
        self.put25v_act = self.get_vol(self.put25k_act)
        self.put10v_act = self.get_vol(self.put10k_act)
        self.atmv_act = self.get_vol(self.fwd)
        self.rr25_f = self.call25v_act - self.put25v_act
        self.rr10_f = self.call10v_act - self.put10v_act
        self.fly25_f = (self.call25v_act + self.put25v_act)/2.0 - self.atmv_act
        self.fly10_f = (self.call10v_act + self.put10v_act)/2.0 - self.atmv_act
        return True
    
    def test_skew(self):
        vols_i = [self.put_10, self.put_25, self.atm_vol, self.call_25,
                  self.call_10]
        strikes_i = [self.put_10_k, self.put_25_k, self.fwd, self.call_25_k,
                     self.call_10_k]
        low_k = max(0, self.fwd*(1 - 2.0*self.atm_vol*sqrt(self.expiry)))
        high_k = self.fwd*(1 + 2.0*self.atm_vol*sqrt(self.expiry))
        strikes = []
        vols =[]
        for i in range(100):
            strike = low_k + (high_k - low_k)/100*i
            strikes.append(strike)
            vols.append(self.get_vol(strike))
        plt.scatter(strikes, vols, alpha=0.6)
        plt.scatter(strikes_i, vols_i, c='red', edgecolor='red')
        plt.show()
        return True
        
    def get_vol(self, k):
        ''' gets vol for strike from the fitted skew
        '''
        return self.beta_0 + self.beta_1*k + self.beta_2*k*k

    def get_strike(self, delta, is_call = True):
        low_k = max(0,self.fwd*(1 - 5.0*self.atm_vol*sqrt(self.expiry)))
        high_k = self.fwd*(1 + 5.0*self.atm_vol*sqrt(self.expiry))
        epsilon = 0.000001
        i = 0
        mid_k = (high_k + low_k)/2.0
        while ((high_k - low_k) >= epsilon) and i < 100:
            mid_k = (high_k + low_k)/2.0
            vol_mid = self.get_vol(mid_k)
            mid_delta = abs(bp.bs_delta(self.spot, mid_k, vol_mid, self.expiry,
                                        is_call, self.ir_d, self.ir_f))
            if (mid_delta > delta):
                if is_call:
                    low_k = mid_k
                else:
                    high_k = mid_k
            else:
                if is_call:
                    high_k = mid_k
                else:
                    low_k = mid_k
            i += 1
        return mid_k

    def __str__(self):
        params = 'input data\nspot: %.4f\tfwd: %.4f\nir dom: %.2f%%\t' \
                 %(self.spot, self.fwd, self.ir_d*100)
        params += 'ir for: %.2f%%\nexpiry (days): %.1f\n' \
                  %(self.ir_f*100, 365.0*self.expiry)
        input_data = 'input params\n\t25d\t10d \nrr\t%4.2f\t%4.2f\n' \
                     %(self.rr_25*100, self.rr_10*100)
        input_data += 'fly\t%4.2f\t%4.2f\n' \
                      %(self.fly_25*100, self.fly_10*100)
        fitted_data = 'fitted params\n\t25d\t10d \nrr\t%4.2f\t%4.2f' \
                      %(self.rr25_f*100, self.rr10_f*100)
        fitted_data += '\nfly\t%4.2f\t%4.2f\n' \
                      %(self.fly25_f*100, self.fly10_f*100)
        header = '\t10d P\t25d P\tatmf\t25d C\t10d C'
        strikes = 'strikes\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f' \
                  %(self.put_10_k, self.put_25_k, self.fwd, self.call_25_k,
                    self.call_10_k)
        vols = 'vols\t%.2f%%\t%.2f%%\t%.2f%%\t%.2f%%\t%.2f%%'\
               %(self.put_10*100, self.put_25*100, self.atm_vol*100,
                 self.call_25*100, self.call_10*100)
        input_table = header + '\n' + strikes + '\n' + vols
        strikes_f = 'strikes\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f' \
                    %(self.put10k_act, self.put25k_act, self.fwd,
                      self.call25k_act, self.call10k_act)
        vols_f = 'vols\t%.2f%%\t%.2f%%\t%.2f%%\t%.2f%%\t%.2f%%'\
                 %(self.put10v_act*100, self.put25v_act*100, self.atmv_act*100,
                   self.call25v_act*100, self.call10v_act*100)
        fitted_table = header + '\n' + strikes_f + '\n' + vols_f
        return params + '\n' + input_data + '\n' + input_table + '\n\n' + \
               fitted_data + '\n' + fitted_table

####################################################################
######
####################################################################
    
class Vol_mkt(object):
    def __init__(self, spot, expiry, atmf, rr_25, rr_10, fly_25, fly_10,
                 ir_d, ir_f):
        self.spot = spot
        self.expiry = expiry
        self.atmf = atmf
        self.ir_d = ir_d
        self.ir_f = ir_f
        self.rr_25 = rr_25
        self.rr_10 = rr_10
        self.fly_25 = fly_25
        self.fly_10 = fly_10

    def interp_skew(self, date):
        ir_d = np.interp(date, self.expiry, self.ir_d)
        ir_f = np.interp(date, self.expiry, self.ir_f)
        atm_vol = np.interp(date, self.expiry, self.atmf)
        rr_25 = np.interp(date, self.expiry, self.rr_25)
        rr_10 = np.interp(date, self.expiry, self.rr_10)
        fly_25 = np.interp(date, self.expiry, self.fly_25)
        fly_10 = np.interp(date, self.expiry, self.fly_10)
        skw = Skew(self.spot, date, ir_d, ir_f, atm_vol, rr_25, rr_10,
                   fly_25, fly_10)
        return skw

    def __str__(self):
        len_mkt = len(self.expiry)
        header = '\ntenor\tatmf\trr25d\trr10d\tfly25d\tfly10d\tdom ir\tfor ir'
        mkt_info = '\n'
        for i in range(len_mkt):
            mkt_info += '%.4f\t%5.2f%%\t%5.2f\t%5.2f\t%5.2f\t' \
                        %(self.expiry[i], self.atmf[i]*100, self.rr_25[i]*100,
                          self.rr_10[i]*100, self.fly_25[i]*100)
            mkt_info += '%5.2f\t%5.2f\t%5.2f\n' \
                        %(self.fly_10[i]*100, self.ir_d[i]*100,
                          self.ir_f[i]*100)
        return header+ mkt_info
