import Event_Gap
import basic_pricer as bp
from math import *
from Vol_Market import Skew
import sys
import gap_event
import gap_event_smile

def ig_uneven_vol(k, s, expiry, ird, irf, curr_v, post_up, post_dn, up_f=1.0):
    p_u = 1.0 / (1.0 + up_f)
    p_d = 1.0 - p_u
    curr_prem = bp.bs_str(s, k, curr_v, expiry, ird, irf)
    gap_low = 0.0
    gap_high = curr_v*sqrt(3.0*expiry/pi)*1.1*max(1, 1.0/up_f)
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

def pre_vol_uneven(k, s, expiry, ird, irf, post_up, post_dn, egap, up_f=1.0):
    p_u = 1.0 / (1.0 + up_f)
    p_d = 1.0 - p_u
    prem_dn = bp.bs_str(s, k*(1 + egap), post_dn, expiry, ird, irf)
    prem_up = bp.bs_str(s, k*(1 - egap*up_f), post_up, expiry, ird, irf)
    temp_prem = prem_dn*p_d + prem_up*p_u
    return bp.implied_vol_str(temp_prem, s, k, expiry, ird, irf)

def ig_uneven_vol_skew(k, curr_v, skew_up, skew_dn, up_f=1.0):
    p_u = 1.0 / (1.0 + up_f)
    p_d = 1.0 - p_u
    s = skew_up.spot
    if s != skew_dn.spot:
        sys.exit('-- Spot not consistent between skews. --')
    expiry = skew_up.expiry
    if expiry != skew_dn.expiry:
        sys.exit('-- Expiry not consistent between skews. --')
    ird = skew_up.ir_d
    irf = skew_up.ir_f
    curr_prem = bp.bs_str(s, k, curr_v, expiry, ird, irf)
    gap_low = 0.00
    gap_high = curr_v*sqrt(2.0*expiry/pi)*1.1*max(1, 1.0/up_f)
    mid_gap = (gap_low + gap_high)/2.0
    epsilon = 0.0000001
    i = 0
    while gap_high - gap_low >= epsilon and i < 100:
        mid_gap = (gap_low + gap_high)/2.0
        k_up = k*(1 - mid_gap*up_f)
        vol_up = skew_up.get_vol(k_up)
        prem_up = bp.bs_str(s, k_up, vol_up, expiry, ird, irf)
        k_dn = k*(1 + mid_gap)
        vol_dn = skew_dn.get_vol(k_dn)
        prem_dn = bp.bs_str(s, k_dn, vol_dn, expiry, ird, irf)
        temp_prem = prem_dn*p_d + prem_up*p_u
        if temp_prem > curr_prem:
            gap_high = mid_gap
        else:
            gap_low = mid_gap
        i += 1
    return mid_gap

def pre_vol_uneven_skew(k, skew_up, skew_dn, egap, up_f=1.0):
    p_u = 1.0 / (1.0 + up_f)
    p_d = 1.0 - p_u
    s = skew_up.spot
    if s != skew_dn.spot:
        sys.exit('-- Spot not consistent between skews. --')
    expiry = skew_up.expiry
    if expiry != skew_dn.expiry:
        sys.exit('-- Expiry not consistent between skews. --')
    ird = skew_up.ir_d
    irf = skew_up.ir_f
    k_up = k*(1 - egap*up_f)
    vol_up = skew_up.get_vol(k_up)
    prem_up = bp.bs_str(s, k_up, vol_up, expiry, ird, irf)
    k_dn = k*(1 + egap)
    vol_dn = skew_dn.get_vol(k_dn)
    prem_dn = bp.bs_str(s, k_dn, vol_dn, expiry, ird, irf)
    temp_prem = prem_dn*p_d + prem_up*p_u
    return bp.implied_vol_str(temp_prem, s, k, expiry, ird, irf)
    
#####
##
#####

def main3():
    ## market data
    s = 10.00
    k = 10.00
    expiry = 1/365
    ird = irf = 0.00
    pre_v = 0.25
    post_v = 0.13
    up_f = 1/2.0
    post_up = 0.10
    post_dn = 0.20

    ## skew market data
    has_skew = True
    if has_skew:
        rr_25 = 1.0/100
        rr_10 = 2.0/100
        fly_25 = 0.25/100
        fly_10 = 1.0/100
    else:
        rr_25 = 0.00/100
        rr_10 = 0.00/100
        fly_25 = 0.00/100
        fly_10 = 0.00/100

    ## implied gap
    post_skew = Skew(s, expiry, ird, irf, post_v, rr_25, rr_10, fly_25, fly_10)
    print()
    print('implied gap')
    ig1 = Event_Gap.implied_gap(k, s, expiry, ird, irf, pre_v, post_v, up_f)
    ig2 = gap_event_smile.implied_gap(k, pre_v, post_skew, up_f)
    print(' orig ig: %.4f%%'%(100*ig1))
    print(' new ig:  %.4f%%'%(100*ig2))
    print()
    ## post vol
    print('post vol')
    postv1 = Event_Gap.post_vol(k, s, expiry, ird, irf, pre_v, ig1, up_f)
    postv2 = gap_event_smile.post_vol(k, post_skew, pre_v, ig2, up_f)
    print(' orig postv: %.4f%%'%(100*postv1))
    print(' new postv:  %.4f%%'%(100*postv2))
    print()
    ## pre vol
    print('pre vol')
    prev1 = Event_Gap.gap_vol(k, s, expiry, ird, irf, post_v, ig1, up_f)
    prev2 = gap_event_smile.pre_vol(k, post_skew, ig2, up_f)
    print(' orig prev: %.4f%%'%(100*prev1))
    print(' new prev:  %.4f%%'%(100*prev2))

    ## test objects
    ev1 = Event_Gap.Event_Skew(k, pre_v, post_skew, up_f)
    ev2 = gap_event_smile.Event(k, pre_v, post_skew, up_f)
    print()
    print('events')
    ## implied gap
    ig1 = ev1.get_implied_gap()
    ig2 = ev2.get_implied_gap()
    print(' orig ig: %.4f%% - %.4f%%'%(100*ig1[0], 100*ig1[1]))
    print(' new ig:  %.4f%% - %.4f%%'%(100*ig2[0], 100*ig2[1]))
    print()
    ig1 = ev1.get_implied_gap()
    ig2 = ev2.get_implied_gap()
    print(' orig ig: %.4f%% - %.4f%%'%(100*ig1[0], 100*ig1[1]))
    print(' new ig:  %.4f%% - %.4f%%'%(100*ig2[0], 100*ig2[1]))
    print()
    ## pre vol
    pre1 = ev1.get_pre_vol(ig1[0])
    pre2 = ev2.get_pre_vol(ig2[0])
    print(' orig prev: %.4f%%'%(100*pre1))
    print(' new prev:  %.4f%%'%(100*pre2))
    print()
    ## post vol
    post1 = ev2.get_post_vol(ig2[0])
    print(' post vol: %.4f%%'%(100*post1))
    ##pre vol smile
    #ev1.pre_vol_smile()
    #ev2.pre_vol_smile()
    ## gap_smile
    #ev1.gap_smile()
    #ev2.naive_gap_smile()
    # compare facotrs
    facts = [1/3, 1/2, 1, 2, 3]
    # ev1.compare_factor(facts, 25)
    # ev2.compare_factor(facts, 25)
    print(ev1)
    print(ev2)
    ev2.post_vol_smile()
    # prevol strike
    strike = 0.475
    while strike <  0.53:
        kpre1 = ev2.get_pre_strike(strike, True)
        kpre2 = ev2.get_pre_strike(strike, False)
        print('delta: %.2f%%  call: %8.4f -- put: %8.4f'%(strike*100, kpre1, kpre2))
        strike += 0.0025
    ev2.prevol_run()

def main():
    ## market data
    spot = 100.00
    strike = 100.00
    expiry = 1/365
    ir_d = ir_f = 0.00
    curr_vol = 0.25
    base_vol = 0.13
    up_fact = 1/2.0
    base_up = 0.10
    base_dn = 0.20

    ## skew market data
    has_skew = False
    if has_skew:
        rr_25 = 1.00/100
        rr_10 = 2.0/100
        fly_25 = 0.25/100
        fly_10 = 1.0/100
    else:
        rr_25 = 0.00/100
        rr_10 = 0.00/100
        fly_25 = 0.00/100
        fly_10 = 0.00/100
    
    ig = Event_Gap.implied_gap(strike, spot, expiry, ir_d, ir_f, curr_vol,
                               base_vol, up_fact)
    print('now: implied gap: %.3f%%'%(100*ig))
    ig2 = ig_uneven_vol(strike, spot, expiry, ir_d, ir_f, curr_vol, base_up,
                        base_dn, up_fact)
    print('uneven implied gap: %.3f%%'%(100*ig2))

    t1 = Skew(spot, expiry, ir_d, ir_f, base_vol, rr_25, rr_10, fly_25, fly_10)
    ig3 = Event_Gap.implied_gap_skew(strike, curr_vol, t1, up_fact)
    print('---')
    print('implied gap w/skew: %.3f%%'%(ig3*100))
    t_up = Skew(spot, expiry, ir_d, ir_f, base_up, -rr_25, -rr_10, fly_25, fly_10)
    t_dn = Skew(spot, expiry, ir_d, ir_f, base_dn, rr_25, rr_10, fly_25, fly_10)
    ig4 = ig_uneven_vol_skew(strike, curr_vol, t_up, t_dn, up_fact)
    print('uneven implied gap w/skew: %.3f%%'%(ig4*100))

    print('---\n\n---')
    pre1 = Event_Gap.gap_vol(strike, spot, expiry, ir_d, ir_f, base_vol, ig,
                             up_fact)
    print('pre vol: %.3f%%'%(100*pre1))
    pre2 = pre_vol_uneven(strike, spot, expiry, ir_d, ir_f, base_up, base_dn,
                          ig2, up_fact)
    print('pre vol uneven: %.3f%%'%(100*pre2))
    print('---')
    pre3 = Event_Gap.gap_vol_skew(strike, t1, ig3, up_fact)
    print('pre vol w/skew: %.3f%%'%(100*pre3))
    pre4 = pre_vol_uneven_skew(strike, t_up, t_dn, ig4, up_fact)
    print('pre vol uneven w/skew: %.3f%%'%(100*pre4))

    print('\n---')
    post1 = Event_Gap.post_vol(strike, spot, expiry, ir_d, ir_f, curr_vol, ig,
                               up_fact)
    print('post vol: %.2f%%'%(post1*100))
    post2 = Event_Gap.post_vol_skew(strike, t1, curr_vol, ig3, up_fact)
    print('post vol w/skew: %.2f%%'%(post2*100))

def main2():
    ## market data
    s = 10.00
    k = 10.00
    expiry = 1/365
    ird = irf = 0.00
    pre_v = 0.4
    post_v = 0.20
    up_f = 1/1.0
    post_up = 0.10
    post_dn = 0.20

    ## implied gap
    print()
    print('implied gap')
    ig1 = Event_Gap.implied_gap(k, s, expiry, ird, irf, pre_v, post_v, up_f)
    ig2 = gap_event.implied_gap(k, s, expiry, ird, irf, pre_v, post_v, up_f)
    print(' orig ig: %.4f%%'%(100*ig1))
    print(' new ig:  %.4f%%'%(100*ig2))
    print()
    ## post vol
    print('post vol')
    postv1 = Event_Gap.post_vol(k, s, expiry, ird, irf, pre_v, ig1, up_f)
    postv2 = gap_event.post_vol(k, s, expiry, ird, irf, pre_v, ig2, up_f)
    print(' orig postv: %.4f%%'%(100*postv1))
    print(' new postv:  %.4f%%'%(100*postv2))
    print()
    ## pre vol
    print('pre vol')
    prev1 = Event_Gap.gap_vol(k, s, expiry, ird, irf, post_v, ig1, up_f)
    prev2 = gap_event.pre_vol(k, s, expiry, ird, irf, post_v, ig2, up_f)
    print(' orig prev: %.4f%%'%(100*prev1))
    print(' new prev:  %.4f%%'%(100*prev2))

    ## test objects
    ev1 = Event_Gap.Event(s, k, expiry, pre_v, post_v, up_f, ird, irf)
    ev2 = gap_event.Event(s, k, expiry, pre_v, post_v, up_f, ird, irf)
    print()
    print('events')
    ## implied gap
    ig1 = ev1.get_implied_gap()
    ig2 = ev2.get_implied_gap()
    print(' orig ig: %.4f%% - %.4f%%'%(100*ig1[0], 100*ig1[1]))
    print(' new ig:  %.4f%% - %.4f%%'%(100*ig2[0], 100*ig2[1]))
    print()
    ig1 = ev1.get_implied_gap()
    ig2 = ev2.get_implied_gap()
    print(' orig ig: %.4f%% - %.4f%%'%(100*ig1[0], 100*ig1[1]))
    print(' new ig:  %.4f%% - %.4f%%'%(100*ig2[0], 100*ig2[1]))
    print()
    ## pre vol
    pre1 = ev1.get_pre_vol(0.03, 1)
    pre2 = ev2.get_pre_vol(0.03, 1)
    print(' orig prev: %.4f%%'%(100*pre1))
    print(' new prev:  %.4f%%'%(100*pre2))
    print()
    ## graph pre_vol smile
    #ev1.pre_vol_smile(20, 2.0, True, 0.02)
    #ev2.pre_vol_smile(20, 1/2.0, True, 0.02)
    ## graph gap smile
    #ev1.gap_smile()
    #ev2.naive_gap_smile()
    ## compare factors
    facts = [1/3, 1/2, 1, 2, 3]
    #ev1.compare_factor(facts, 25)
    #ev2.compare_factor(facts, 25)
    ## post_vol
    pv2 = ev2.get_post_vol(ig2[0])
    print('post vol: %.4f%%'%(100*pv2))
    ## print data
    #print(ev1)
    #print()
    #print(ev2)
    ## post_vol smile
    #ev2.post_vol_smile()
    # prevol strike
    '''
    strike = 0.475
    while strike <  0.53:
        kpre1 = ev2.get_pre_strike(strike, True)
        kpre2 = ev2.get_pre_strike(strike, False)
        print('delta: %.2f%%  call: %8.4f -- put: %8.4f'%(strike*100, kpre1, kpre2))
        strike += 0.0025
    '''
    # vol run
    ev2.prevol_run()
    
if __name__ == '__main__':
    main2()
