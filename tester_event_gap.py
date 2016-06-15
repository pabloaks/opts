import Event_Gap 
import basic_pricer
from Vol_Market import Skew, Vol_mkt
from Event_Gap import Event, Event_Skew

## market inputs
spot = 1.0
strike = 1.0
expiry = 30/365.0
ir_d = 0.0
ir_f = 0.0
atm_vol = 0.13
curr_vol = 0.15
up_factor = 5.0
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

' test skew object - Vol_Market'
t1 = Skew(spot, expiry, ir_d, ir_f, atm_vol, rr_25, rr_10, fly_25, fly_10)

if False:
    print(t1)
    print()
    print('from fitted curve')
    ## test 10d call
    call_10d_k = t1.get_strike(0.10,True)
    call_10d_vol = t1.get_vol(call_10d_k)
    print('10d call strike: %.4f'%(call_10d_k))
    print('vol: %.2f%%'%(100*call_10d_vol))
    ## test 25d call
    call_25d_k = t1.get_strike(0.25,True)
    call_25d_vol = t1.get_vol(call_25d_k)
    print('25d call strike: %.4f'%(call_25d_k))
    print('vol: %.2f%%'%(100*call_25d_vol))
    ## test 25d put
    put_25d_k = t1.get_strike(0.25,False)
    put_25d_vol = t1.get_vol(put_25d_k)
    print('25d put strike: %.4f'%(put_25d_k))
    print('vol: %.2f%%'%(100*put_25d_vol))
    ## test 10d put
    put_10d_k = t1.get_strike(0.10,False)
    put_10d_vol = t1.get_vol(put_10d_k)
    print('10d put strike: %.4f'%(put_10d_k))
    print('vol: %.2f%%'%(100*put_10d_vol))
    ## test delta for 10d put strikes, and vol for them as well...
    ##put_10d_k_fitted = 

    t1.test_skew()

if False:
    ' test event gap, just checking functions '
    ' no skew '
    print('\nTEST formulas for event gap w/now skew')
    eg1 = Event_Gap.implied_gap(strike, spot, expiry, ir_d, ir_f, curr_vol, atm_vol)
    print('%.4f%%'%(100*eg1))
    up_factor = 2.0
    eg2 = Event_Gap.implied_gap(strike, spot, expiry, ir_d, ir_f, curr_vol, atm_vol, up_factor)
    print('down gap: \t%.4f%% \nup gap: \t%.4f%%'%(100*eg2, up_factor*100*eg2))
    EM = 2*up_factor*eg2/(1+up_factor)
    print('exp. move: \t%.4f%%'%(100*EM))
    pre_vol = Event_Gap.gap_vol(strike, spot, expiry, ir_d, ir_f, atm_vol, eg1)
    print('\npre vol: %.2f%% \ncurr vol: %.2f%%'%(100*pre_vol, 100*curr_vol))
    pre_vol2 = Event_Gap.gap_vol(strike, spot, expiry, ir_d, ir_f, atm_vol, eg2, up_factor)
    print('\npre vol: %.2f%% \ncurr vol: %.2f%%'%(100*pre_vol2, 100*curr_vol))

    print('\n\nTEST formulas for event gap w/skew')
    up_factor = 2.0
    eg3 = Event_Gap.implied_gap_skew(strike, curr_vol, t1)
    print('%.4f%%'%(100*eg3))
    up_factor = 2.0
    eg4 = Event_Gap.implied_gap_skew(strike, curr_vol, t1, up_factor)
    print('down gap: \t%.4f%% \nup gap: \t%.4f%%'%(100*eg4, up_factor*100*eg4))
    EM = 2*up_factor*eg4/(1+up_factor)
    print('exp. move: \t%.4f%%'%(100*EM))
    pre_vol = Event_Gap.gap_vol_skew(strike, t1, eg3)
    print('\npre vol: %.2f%% \ncurr vol: %.2f%%'%(100*pre_vol, 100*curr_vol))
    pre_vol2 = Event_Gap.gap_vol_skew(strike, t1, eg4, up_factor)
    print('\npre vol: %.2f%% \ncurr vol: %.2f%%'%(100*pre_vol2, 100*curr_vol))

if False:
    ' test Event object '
    ev1 = Event(spot, strike, expiry, curr_vol, atm_vol, up_factor , ir_d, ir_f)
    ev2 = Event_Skew(strike, curr_vol, t1, up_factor)
    print('event gap')
    print(ev1.get_implied_gap())
    print(ev2.get_implied_gap())
    print('pre vol for given gap')
    g = ev1.get_implied_gap()[0]
    print(ev1.get_pre_vol(g))
    print(ev2.get_pre_vol(g))
    print(ev1.get_pre_vol(0.01))
    print(ev2.get_pre_vol(0.01))
    ev1.pre_vol_smile()
    ev2.pre_vol_smile()
    ev1.gap_smile()
    ev2.gap_smile()
    ev1.compare_factor([1,2,1/3.0])
    ev2.compare_factor([1,2,1/3.0])
    print('\n')
    print(ev1)
    print('\n\n')
    print(ev2)

' test vol market and interp in there '
if True:
    spot = 1.00
    strike = 1.00
    expiry = 10/365.0
    ir_d = 0.0
    ir_f = 0.0
    atm_vol = 0.12
    curr_vol = 0.14
    rr_25 = 1.00/100
    rr_10 = 2.00/100
    fly_25 = 0.25/100
    fly_10 = 1.00/100
    expiry = [1/365, 7/365, 30/365]
    atmf = [0.10, 0.1025, 0.1075]
    ir_d = [0.0, 0.0, 0.0]
    ir_f = [0.0, 0.0, 0.0]
    rr_25 = [1.25/100, 1.5/100, 2.0/100]
    rr_10 = [2.25/100, 2.75/100, 3.5/100]
    fly_25 = [0.25/100, 0.3/100, 0.40/100]
    fly_10 = [0.75/100, 0.9/100, 1.25/100]
    mm = Vol_mkt(spot, expiry, atmf, rr_25, rr_10, fly_25, fly_10, ir_d, ir_f)
    t2 = mm.interp_skew(7/365)
    print(t2)
    print(mm)
