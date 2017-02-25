from opts import basic_pricer as bp

def string2dec(num):
    return "{:,}".format(float('%.2f'%(num)))

def realized_pl(spot_series, notional, strike, vol, expiry, rate_dom, rate_for,
                hedge_vol, is_call):
    '''calculates the domestic P/L, i.e. USD for USD/XXX, after delta
    hedging at every time stamp assumes bs delta done at the same price
    using hedge_vol parameter to calculate
    ''' 
    delta = 0
    hedge_cost = 0
    num_spot = len(spot_series)
    df_dom = bp.df(rate_dom, expiry)
    
    option_premium = notional/df_dom*bp.bs_price(spot_series[0], strike, vol,
                                                 expiry, is_call, rate_dom,
                                                 rate_for, False)
    if is_call:
        option_payout = max(0, spot_series[-1] - strike) * notional / \
                        spot_series[-1]
    else:
        option_payout = max(0, strike - spot_series[-1]) * notional / \
                        spot_series[-1]

    for i in range(1,num_spot):
        temp_exp = expiry * (num_spot - i) / (num_spot - 1)
        fwd_factor = bp.df(rate_dom, temp_exp) / bp.df(rate_for, temp_exp)
        temp_delta = bp.bs_delta(spot_series[i-1], strike, hedge_vol, temp_exp,
                                 is_call, rate_dom, rate_for) * notional \
                                 * -strike
        hedge_cost += (temp_delta - delta) / (spot_series[i-1] * fwd_factor)
        delta = temp_delta
    hedge_cost -= delta/spot_series[-1]

    return option_payout + hedge_cost - option_premium

def breakeven_vol(spot_series, strike, hedge_vol, expiry, rate_dom, rate_for):
    ''' calculates implied vol that would have resulted in a zero P/L
    asuming delta hedging at hedge_vol for very far OTM options b.e. vol
    can be very unstable, do not use ITM to calculate you can end up
    with negative b.e. vol
    '''
    delta = 0
    hedge_cost = 0
    num_spot = len(spot_series)
    df_dom = bp.df(rate_dom, expiry)
    fwd_spot = spot_series[0] * bp.df(rate_dom, expiry) / bp.df(rate_for, expiry)
    if fwd_spot < strike:
        is_call = True
    else:
        is_call = False
    if is_call:
        option_payout = max(0, spot_series[-1] - strike) / spot_series[-1]
    else:
        option_payout = max(0, strike - spot_series[-1]) / spot_series[-1]

    for i in range(1,num_spot):
        temp_exp = expiry * (num_spot - i) / (num_spot - 1)
        fwd_factor = bp.df(rate_dom, temp_exp) / bp.df(rate_for, temp_exp)
        temp_delta = bp.bs_delta(spot_series[i-1], strike, hedge_vol, temp_exp,
                                 is_call, rate_dom, rate_for) * -strike
        hedge_cost += (temp_delta - delta) / (spot_series[i-1] * fwd_factor)
        delta = temp_delta
    hedge_cost -= delta/spot_series[-1]
    option_premium = (hedge_cost + option_payout) * df_dom 

    if option_premium > 0:
        be_vol = bp.implied_vol_bs(option_premium, spot_series[0], strike,
                                   expiry, is_call, rate_dom, rate_for)
    else:
        be_vol = -bp.implied_vol_bs(-option_premium, spot_series[0], strike,
                                    expiry, is_call, rate_dom, rate_for)
    return be_vol

def realized_pl_end(spot_series, notional, strike, vol, st_dt, ed_dt, rate_dom,
                    rate_for, hedge_vol, is_call, sell_vol=88.88):
    ''' calculates P/L for option that is sold before maturity
    if no sell_vol is given it assumes it gets sold at initial vol'''
    delta = 0
    hedge_cost = 0
    num_spot = len(spot_series)
    df_dom = bp.df(rate_dom, st_dt)
    term = st_dt - ed_dt
    if sell_vol == 88.88:
        sell_vol = vol

    op_prem = notional / df_dom * bp.bs_price(spot_series[0], strike, vol,
                                              st_dt, is_call, rate_dom,
                                              rate_for, False)
    if ed_dt == 0:
        pp = realized_pl(spot_series, notional, strike, vol, st_dt, rate_dom,
                         rate_for, hedge_vol, is_call)
        return pp

    df_dom = bp.df(rate_dom, ed_dt)
    op_payout = notional / df_dom * bp.bs_price(spot_series[-1], strike,
                                                sell_vol, ed_dt, is_call,
                                                rate_dom, rate_for, False)
    
    for i in range(1, num_spot + 1):
        temp_exp = term * (num_spot - i) / (num_spot - 1) + ed_dt
        fwd_factor = bp.df(rate_dom, temp_exp) / bp.df(rate_for, temp_exp)
        temp_delta = bp.bs_delta(spot_series[i-1], strike, hedge_vol, temp_exp,
                                 is_call, rate_dom, rate_for) * notional \
                                 * -strike
        hedge_cost += (temp_delta - delta) / (spot_series[i-1] * fwd_factor)
        delta = temp_delta
        
    hedge_cost -= delta/(spot_series[-1] * fwd_factor)
    return op_payout + hedge_cost - op_prem

def breakeven_vol_end(spot_series, strike, hedge_vol, st_dt, ed_dt, rate_dom,
                      rate_for, sell_vol=88.88):
    delta = 0
    hedge_cost = 0
    num_spot = len(spot_series)
    df_dom = bp.df(rate_dom, st_dt)
    term = st_dt - ed_dt
    fwd_spot = spot_series[0] * bp.df(rate_dom, st_dt) / bp.df(rate_for, st_dt)

    if fwd_spot < strike:
        is_call = True
    else:
        is_call = False

    if sell_vol == 88.88:
        sell_vol = hedge_vol

    if ed_dt == 0:
        be = breakeven_vol(spot_series, strike, hedge_vol, st_dt, rate_dom,
                           rate_for)
        return be

    df_dom = bp.df(rate_dom, ed_dt)
    op_payout = bp.bs_price(spot_series[-1], strike, sell_vol, ed_dt,
                                is_call, rate_dom, rate_for, False) / df_dom

    for i in range(1, num_spot + 1):
        temp_exp = term * (num_spot - i) / (num_spot - 1) + ed_dt
        fwd_factor = bp.df(rate_dom, temp_exp) / bp.df(rate_for, temp_exp)
        temp_delta = bp.bs_delta(spot_series[i-1], strike, hedge_vol, temp_exp,
                                 is_call, rate_dom, rate_for) * -strike
        hedge_cost += (temp_delta - delta) / (spot_series[i-1] * fwd_factor)
        delta = temp_delta
    hedge_cost -= delta/(spot_series[-1] * fwd_factor)
    option_premium = (hedge_cost + op_payout) * df_dom 

    if option_premium > 0:
        be_vol = bp.implied_vol_bs(option_premium, spot_series[0], strike,
                                   st_dt, is_call, rate_dom, rate_for)
    else:
        be_vol = -bp.implied_vol_bs(-option_premium, spot_series[0], strike,
                                    st_dt, is_call, rate_dom, rate_for)
    return be_vol
