import basic_pricer as bp
from math import *
import matplotlib.pyplot as plt
import Vol_Market as vm

def implied_gap(k, s, expiry, ird, irf, pre_v, post_up, post_dn, up_f=1.0):
    p_u = 1.0 / (1.0 + up_f)
    p_d = 1.0 - p_u
    curr_prem = bp.bs_str(s, k, pre_v, expiry, ird, irf)
    gap_low = 0.0
    gap_high = pre_v*sqrt(3.0*expiry/pi)*1.1*max(1, 1.0/up_f)
    mid_gap = (gap_low + gap_high)/2.0
    epsilon = 0.0000001
    i = 0
    while gap_high - gap_low >= epsilon and i < 100:
        mid_gap = (gap_low + gap_high) / 2.0
        prem_dn = bp.bs_str(s, k*(1 + mid_gap), post_dn, expiry, ird, irf)
        prem_up = bp.bs_str(s, k*(1 - mid_gap*up_f), post_up, expiry, ird, irf)
        temp_prem = prem_dn*p_d + prem_up*p_u
        if temp_prem > curr_prem:
            gap_high = mid_gap
        else:
            gap_low = mid_gap
        i += 1
    return mid_gap

## testing, using a vol factor, post_up has to be a factor of post_dn
def post_vol(k, s, expiry, ird, irf, pre_v, egap, vol_f, up_f=1.0):
    p_u = 1.0 / (1.0 + up_f)
    p_d = 1.0 - p_u
    prem_b = bp.bs_str(s, k, pre_v, expiry, ird, irf)
    vol_low = 0.0
    vol_high = 10*pre_v
    mid_vol = (vol_low + vol_high) / 2.0
    epsilon = 0.000000001
    i = 0
    while vol_high - vol_low >= epsilon and i < 100:
        mid_vol = (vol_low + vol_high) / 2.0
        prem_dn = bp.bs_str(s, k*(1 + egap), mid_vol, expiry, ird, irf)
        prem_up = bp.bs_str(s, k*(1 - egap*up_f), mid_vol*vol_f, expiry, ird,
                            irf)
        temp_prem =  prem_dn*p_d + prem_up*p_u
        if temp_prem > prem_b:
            vol_high = mid_vol
        else:
            vol_low = mid_vol
        i += 1
    return mid_vol

def pre_vol(k, s, expiry, ird, irf, post_up, post_dn, egap, up_f=1.0):
    p_u = 1.0 / (1.0 + up_f)
    p_d = 1.0 - p_u
    prem_dn = bp.bs_str(s, k*(1 + egap), post_dn, expiry, ird, irf)
    prem_up = bp.bs_str(s, k*(1 - egap*up_f), post_up, expiry, ird, irf)
    temp_prem = prem_dn*p_d + prem_up*p_u
    return bp.implied_vol_str(temp_prem, s, k, expiry, ird, irf)

''' *********************************************************************
********************************************************************* '''
class Event(object):

    def __init__(self, s, k, expiry, pre_vol, post_up, post_dn, up_f=1.0,
                 ird=0.0, irf=0.0):
        self.s = s
        self.k = k
        self.expiry = expiry
        self.pre_vol = pre_vol
        self.post_up = post_up
        self.post_dn = post_dn
        self.up_f = up_f
        self.ird = ird
        self.irf = irf
        self.fwd = s * bp.df(ird, expiry) / bp.df(irf, expiry)
        self.imp_gap = self.get_implied_gap()
        self.vol_f = post_up/post_dn

    def get_implied_gap(self, up_f=88.8):
        if up_f == 88.8:
            up_f = self.up_f
        temp = implied_gap(self.k, self.s, self.expiry, self.ird, self.irf,
                           self.pre_vol, self.post_up, self.post_dn, up_f)
        return (temp, temp*up_f)

    def prevol_run(self):
        put10 = self.get_pre_vol_k(self.get_pre_strike(0.10, False))
        put25 = self.get_pre_vol_k(self.get_pre_strike(0.25, False))
        call25 = self.get_pre_vol_k(self.get_pre_strike(0.25, True))
        call10 = self.get_pre_vol_k(self.get_pre_strike(0.10, True))
        atmf = self.get_pre_vol_k(self.fwd)
        rr25 = call25 - put25
        rr10 = call10 - put10
        fly25 = (call25 + put25)/2 - atmf
        fly10 = (call10 + put10)/2 - atmf
        pre_skew = vm.Skew(self.s, self.expiry, self.ird, self.irf, atmf, rr25,
                           rr10, fly25, fly10)
        return pre_skew

    def get_pre_vol_k(self, k):
        return pre_vol(k, self.s, self.expiry, self.ird, self.irf, self.post_up,
                       self.post_dn, self.imp_gap[0], self.up_f)

    def get_pre_vol(self, gap, up_f=88.8):
        if up_f == 88.8:
            up_f = self.up_f
        return pre_vol(self.k, self.s, self.expiry, self.ird, self.irf,
                       self.post_up, self.post_dn, gap, up_f)

    def get_post_vol(self, gap, up_f=88.8, vol_f=88.8):
        if up_f == 88.8:
            up_f = self.up_f
        if vol_f == 88.8:
            vol_f = self.vol_f
        return post_vol(self.k, self.s, self.expiry, self.ird, self.irf,
                        self.pre_vol, self.gap, vol_f, up_f)

    def get_pre_strike(self, delta, is_call=True):
        ' get strike pre-event for given delta '
        low_k = max(0, self.fwd*(1 - 5*self.pre_vol*sqrt(self.expiry)))
        high_k = self.fwd*(1 + 5*self.pre_vol*sqrt(self.expiry))
        epsilon = 0.000001
        i = 0
        mid_k = (high_k + low_k)/2
        while high_k - low_k >= epsilon and i < 100:
            mid_k = (high_k + low_k)/2
            vol_mid = self.get_pre_vol_k(mid_k)
            mid_delta = abs(bp.bs_delta(self.s, mid_k, vol_mid, self.expiry,
                                        is_call, self.ird, self.irf))
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

    def post_vol_smile(self, num_k=10, up_f=88.8, plot=True, over_gap=88.8,
                       volf_f=88.8):
        low_k = self.fwd*(1 - 2*self.pre_vol*sqrt(self.expiry))
        inc = (self.fwd - low_k)/num_k
        strikes = []
        vols = []
        if up_f == 88.8:
            up_f = self.up_f
        if vol_f == 88.8:
            vol_f = self.vol_f
        for i in range(num_k*2 + 1):
            strikes.append(low_k + inc*i)
        if over_gap == 88.8:
            strike_gap = implied_gap(self.k, self.s, self.expiry, self.ird,
                                     self.irf, self.pre_vol, self.post_dn*vol_f,
                                     self.post_dn, up_f)

        implied_gap(k, s, expiry, ird, irf, pre_v, post_up, post_dn, up_f=1.0)
        
        






















