import basic_pricer as bp
import datetime
import backtest as bt
  

def main():
    notional = 100000000
    spot = 13.0
    strike = 13.0
    vol = 0.115
    rate_dom = 0.0
    rate_for = 0.0
    hedge_vol = 0.12
    sell_vol = 0.13
    start = datetime.date(2016, 8, 6)
    end = datetime.date(2016, 8, 21)
    maturity = datetime.date(2016, 8, 27)
    st_dt = (maturity - start) / datetime.timedelta(365, 0, 0)
    ed_dt = (maturity - end) / datetime.timedelta(365, 0, 0)
    expiry = st_dt - ed_dt
    loadFromFile = True
    if loadFromFile:
        f = open('sim_prices.txt','rt')
        prices = []
        for line in f:
            prices.append(float(line.strip('\n')))
        f.close()

    call_pl = bt.realized_pl_end(prices, notional, strike, vol, st_dt, ed_dt,
                                 rate_dom, rate_for, hedge_vol, True, sell_vol)
    print('call: %.2f' %(call_pl))
    
    put_pl = bt.realized_pl_end(prices, notional, strike, vol, st_dt, ed_dt,
                                rate_dom, rate_for, hedge_vol, False, sell_vol)
    print('put: %.2f' %(put_pl))
    
    be_vol = bt.breakeven_vol_end(prices, strike, hedge_vol, st_dt, ed_dt,
                               rate_dom, rate_for, sell_vol)
    print('be vol: %.2f'%(100*be_vol))
    be_vol2 = bt.breakeven_vol(prices, strike, hedge_vol, st_dt, rate_dom,
                               rate_for)
    print('be vol: %.2f'%(100*be_vol2))
    


if __name__ == '__main__':
    main()
    
            

    
