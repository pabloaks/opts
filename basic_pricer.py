from math import *
#from scipy.stats import norm

def df(rate,expiry):
    ' plain discount factor '
    return 1 / ((1 + rate)**expiry)

def phi(x):
    ' std norm cdf, much faster than loading scipy.stats '
    ' tested form -10 to 10, small error but there is a difference '
    a1 =  0.254829592; a2 = -0.284496736; a3 =  1.421413741
    a4 = -1.453152027; a5 =  1.061405429; p  =  0.3275911
    #xx = x
    sign = 1
    if x < 0:
        sign = -1
    x = abs(x)/sqrt(2.0)
    t = 1.0 / (1.0 + p*x)
    y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t*exp(-x*x)
    return 0.5*(1.0 + sign*y)
    #return norm.cdf(xx)

def norm_CDF_inv(p):
    c = [2.515517, 0.802853, 0.010328]
    d = [1.432788, 0.189269, 0.001308]
    if p < 0.5:
        t = sqrt(-2.0*log(p))
        t = t - ((c[2]*t + c[1])*t + c[0])/(((d[2]*t + d[1])*t + d[0])*t + 1.0)
        return -t
    else:
        t = sqrt(-2.0*log(1-p))
        t = t - ((c[2]*t + c[1])*t + c[0])/(((d[2]*t + d[1])*t + d[0])*t + 1.0)
        return t

def bs_price(spot, strike, vol, expiry, is_call = True, ir_d = 0.00,
             ir_f = 0.00, is_prem_for = False):
    ' black-scholes for fx, premium is discounted to t=0 '
    ' default premium is domestic, i.e. USD for USD/XXX '
    ' same with rates dom/for, might eb other way in books '
    ' premium is % of notional in that ccy '
    fwd = spot * df(ir_d,expiry) / df(ir_f,expiry)
    d1 = (log(fwd/strike) + vol**2*expiry/2) / (vol*sqrt(expiry))
    d2 = d1 - vol*sqrt(expiry)
    if is_prem_for:
        div_by = strike/df(ir_d,expiry)
    else:
        div_by = spot/df(ir_f,expiry)
    if is_call:
        return (fwd*phi(d1) - strike*phi(d2))/div_by
    else:
        return (strike*phi(-d2) - fwd*phi(-d1))/div_by

def bs_call(spot, strike, vol, expiry, ir_d = 0.00, ir_f = 0.00,
            is_prem_for = False):
    ' wrapper for price of call bs formula '
    return bs_price(spot, strike, vol, expiry, True, ir_d, ir_f, is_prem_for)

def bs_put(spot, strike, vol, expiry, ir_d = 0.00, ir_f = 0.00,
           is_prem_for = False):
    ' wrapper for price of put bs formula '
    return bs_price(spot, strike, vol, expiry, False, ir_d, ir_f, is_prem_for)

def bs_str(spot, strike, vol, expiry, ir_d = 0.00, ir_f = 0.00,
           is_prem_for = False):
    ' wrapper for price of put bs formula '
    return (bs_price(spot, strike, vol, expiry, True, ir_d, ir_f, is_prem_for) +
            bs_price(spot, strike, vol, expiry, False, ir_d, ir_f, is_prem_for))

def bs_delta(spot, strike, vol, expiry, is_call = True, ir_d = 0.00,
             ir_f = 0.00):
    ' analytic bs delta of vanilla option '
    fwd = spot * df(ir_d,expiry) / df(ir_f,expiry)
    d1 = (log(fwd/strike) + vol**2*expiry/2.0) / (vol*sqrt(expiry))
    if is_call:
        return phi(d1)
    else:
        return phi(d1) - 1.0

def bs_strike(spot, delta, vol, expiry, is_call = True, ir_d = 0.00,
              ir_f = 0.00, is_prem_for = False):
    fwd = spot * df(ir_d,expiry) / df(ir_f,expiry)
    if is_call:
        return fwd/exp(norm_CDF_inv(delta)*vol*sqrt(expiry) - vol**2*expiry/2)
    else:
        return fwd/exp(norm_CDF_inv(-delta + 1)*vol*sqrt(expiry) -
                       vol**2*expiry/2)

def implied_vol_bs(price, spot, strike, expiry, is_call = True, ir_d = 0.00,
                   ir_f = 0.00, is_prem_for = False, vol_high = 2.00):
    ' calculates implied vol using the bi-section method '
    epsilon  = 0.00000001
    low_vol = 0.00
    high_vol = vol_high
    i = 0
    while ((high_vol - low_vol) >= epsilon) and i < 100:
        mid_vol = (low_vol + high_vol)/ 2.0
        if bs_price(spot, strike, mid_vol, expiry, is_call, ir_d, ir_f,
                    is_prem_for) > price:
            high_vol = mid_vol
        else:
            low_vol = mid_vol
        i += 1
    return mid_vol

def implied_vol_str(price, spot, strike, expiry, ir_d = 0.00, ir_f = 0.00,
                    is_prem_for = False, vol_high = 2.00):
    ' calculates implied vol for straddle using the bi-section method '
    epsilon  = 0.00000001
    low_vol = 0.00
    high_vol = vol_high
    i = 0
    while ((high_vol - low_vol) >= epsilon) and i < 100:
        mid_vol = (low_vol + high_vol)/ 2.0
        if bs_str(spot, strike, mid_vol, expiry, ir_d, ir_f,
                  is_prem_for) > price:
            high_vol = mid_vol
        else:
            low_vol = mid_vol
        i += 1
    return mid_vol

def realized_vol(prices, expiry_yrs):
    ' calculates realized vol, takes price array, start and end time to expiry in years '
    ' assumes prices are equally spaced from start to time '
    ' need a function to take uneven spaced time series and fill it '
    sum_ret = 0.0
    for i in range(1,len(prices)):
        temp = prices[i]/prices[i-1] - 1
        sum_ret += (prices[i]/prices[i-1] - 1)**2
    return sqrt(sum_ret/(expiry_yrs))
