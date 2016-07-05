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

    def get_implied_gap(self, up_f=88.8):
        if up_f == 88.8:
            up_f = self.up_f
        temp = implied_gap(self.k, self.s, self.expiry, self.ird, self.irf,
                           self.pre_vol, self.post_up, self.post_dn, up_f)
        return (temp, temp*up_f)

























