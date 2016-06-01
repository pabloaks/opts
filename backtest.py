import basic_pricer

def realized_pl(spot_series, notional, strike, vol, expiry, rate_dom, rate_for, hedge_vol, is_call):
    ' calculates the domestic P/L, i.e. USD for USD/XXX, after delta hedging at every time stamp '
    ' assumes bs delta done at the same price, using hedge_vol parameter to calculate '
    delta = 0
    hedge_cost = 0
    num_spot = len(spot_series)
    df_dom = basic_pricer.df(rate_dom, expiry)
    
    option_premium = notional * basic_pricer.bs_price(spot_series[0], strike, vol, expiry, is_call,
                                                      rate_dom, rate_for, False) /df_dom
    if is_call:
        option_payout = max(0, spot_series[-1] - strike) * notional / spot_series[-1]
    else:
        option_payout = max(0, strike - spot_series[-1]) * notional / spot_series[-1]

    for i in range(1,num_spot):
        temp_exp = expiry * (num_spot - i) / (num_spot - 1)
        fwd_factor = basic_pricer.df(rate_dom, temp_exp) / basic_pricer.df(rate_for, temp_exp)
        temp_delta = -basic_pricer.bs_delta(spot_series[i-1], strike, hedge_vol, temp_exp, is_call,
                                            rate_dom, rate_for) * notional * strike
        hedge_cost += (temp_delta - delta) / (spot_series[i-1] * fwd_factor)
        delta = temp_delta
    hedge_cost -= delta/spot_series[-1]

    return option_payout + hedge_cost - option_premium

def breakeven_vol(spot_series, strike, hedge_vol, expiry, rate_dom, rate_for):
    ' calculates implied vol that would have resulted in a zero P/L asuming delta hedging at hedge_vol '
    ' for very far OTM options b.e. vol can be very unstable, do not use ITM to calculate '
    ' you can end up with negative b.e. vol '
    delta = 0
    hedge_cost = 0
    num_spot = len(spot_series)
    df_dom = basic_pricer.df(rate_dom, expiry)
    fwd_spot = spot_series[0] * basic_pricer.df(rate_dom, expiry) / basic_pricer.df(rate_for, expiry)
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
        fwd_factor = basic_pricer.df(rate_dom, temp_exp) / basic_pricer.df(rate_for, temp_exp)
        temp_delta = -basic_pricer.bs_delta(spot_series[i-1], strike, hedge_vol, temp_exp, is_call,
                                            rate_dom, rate_for) * strike
        hedge_cost += (temp_delta - delta) / (spot_series[i-1] * fwd_factor)
        delta = temp_delta
    hedge_cost -= delta/spot_series[-1]
    option_premium = (hedge_cost + option_payout) * df_dom 

    if option_premium > 0:
        be_vol = basic_pricer.implied_vol_bs(option_premium, spot_series[0], strike, expiry,
                                             is_call, rate_dom, rate_for)
    else:
        be_vol = -basic_pricer.implied_vol_bs(-option_premium, spot_series[0], strike, expiry,
                                             is_call, rate_dom, rate_for)
    return be_vol

