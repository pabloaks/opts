import basic_pricer as bp
from math import *
import matplotlib.pyplot as plt
from Vol_Market import Skew

## big question about bumping spot or strike, theoretically should be
## bumping spot but then results are "tricky", not even... but then
## again they are not even for a simple cash trade because the FX risk
## on the P/L in order to keep it "neutral" (even) I am bumping the
## strikes, this way there is no FX risk on P/L because spot never moves
## so for risk management you have to take into account your funding ccy
## but I don't believe you should to analyze what gap market is pricing

## for this reason doinf everything in local ccy premium, doing in forgn
## ccy would be equivalent i think might be a good idea to test with an
## option in different asset (should do stox or rates)

## *** another thing to think ***
## think technically instead of bumping strike would need to bump spot to
## calculate estimated move and adjust strike by that amount.
## i.e. move = spot*gap. move up -> strike_up = strike - move,
## this way everything is more balanced
## a 5% move is the same for a 95 strike and a 105 strike when spot is 100

def implied_gap(k, s, expiry, ird, irf, curr_v, base_v, up_f=1.0):
    ''' will bump the strike by the event gap, instead of the spot, this
    way there is no need to worry about the currency of the p/l, since
    spot is not moving need to think about this about more but otherwise
    results seems off, too uneven 
    up factor = magnitude move up / magnitude move down
    returns magnitude of move down
    '''
    p_u = 1.0 / (1.0 + up_f)
    p_d = 1.0 - p_u
    curr_prem = bp.bs_str(s, k, curr_v, expiry, ird, irf)
    gap_low = 0.0
    gap_high = curr_v*sqrt(3.0*expiry/pi)*1.1*max(1,1.0/up_f)
    ## for low strikes can potentially pass a -ve strike in bs_str()
    ## for very high up_factor, so need to be careful,
    ## and way to control it is with gap_high /// (looks ok now)
    mid_gap = (gap_low + gap_high) / 2.0
    epsilon = 0.000000001
    i = 0
    while gap_high - gap_low >= epsilon and i < 100:
        mid_gap = (gap_low + gap_high) / 2.0
        prem_dn = bp.bs_str(s, k*(1 + mid_gap), base_v, expiry, ird, irf)
        prem_up = bp.bs_str(s, k*(1 - mid_gap*up_f), base_v, expiry, ird, irf)
        temp_prem = prem_dn*p_d + prem_up*p_u
        if temp_prem > curr_prem:
            gap_high = mid_gap
        else:
            gap_low = mid_gap
        i += 1
    return mid_gap
    
def implied_gap_skew(k, curr_v, post_skew, up_fact=1.0):
    ''' assuming we know the skew of the post vol, and we observe pre vol
    for given strike
    '''
    p_u = 1.0 / (1.0 + up_fact)
    p_d = 1.0 - p_u
    spot = post_skew.spot
    expiry = post_skew.expiry
    ir_d = post_skew.ir_d
    ir_f = post_skew.ir_f
    curr_prem = bp.bs_str(spot, k, curr_v, expiry, ir_d, ir_f)
    gap_low = 0.0
    gap_high = curr_v*sqrt(3.0*expiry/pi)*1.1*max(1,1.0/up_fact)
    mid_gap = (gap_low + gap_high) / 2.0
    epsilon = 0.000000001
    i = 0
    while ((gap_high - gap_low) >= epsilon) and i < 100:
        mid_gap = (gap_low + gap_high) / 2.0
        up_gap_k = k*(1 - mid_gap*up_fact)
        down_gap_k = k*(1 + mid_gap)
        up_gap_vol = post_skew.get_vol(up_gap_k)
        down_gap_vol = post_skew.get_vol(down_gap_k)
        temp_prem = (bp.bs_str(spot, up_gap_k, up_gap_vol, expiry, ir_d, ir_f)
                     *p_u +
                     bp.bs_str(spot, down_gap_k, down_gap_vol, expiry, ir_d,
                               ir_f)*p_d)
        if temp_prem > curr_prem:
            gap_high = mid_gap
        else:
            gap_low = mid_gap
        i += 1
    return mid_gap

def post_vol(k, spot, expiry, ird, irf, pre_v, egap, up_f=1.0):
    ''' calculates post vol
    '''
    ## not sure temp_prem is monotonic fn of vol
    ## for big gaps post_vol doesnt always match
    ## unstable solutions so get some errors
    ## need to add check for prem(pre_v) > gap
    p_u = 1.0 / (1.0 + up_f)
    p_d = 1.0 - p_u
    prem_b = bp.bs_str(spot, k, pre_v, expiry, ird, irf)
    vol_low = 0.0
    vol_high = 10*pre_v
    mid_vol = (vol_low + vol_high) / 2.0
    epsilon = 0.000000001
    i = 0
    while vol_high - vol_low >= epsilon and i < 100:
        mid_vol = (vol_low + vol_high) / 2.0
        prem_dn = bp.bs_str(spot, k*(1 + egap), mid_vol, expiry, ird, irf)
        prem_up = bp.bs_str(spot, k*(1 - egap*up_f), mid_vol, expiry, ird, irf)
        temp_prem =  prem_dn*p_d + prem_up*p_u
        if temp_prem > prem_b:
            vol_high = mid_vol
        else:
            vol_low = mid_vol
        i += 1
    return mid_vol

def post_vol_skew(k, post_s, pre_v, egap, up_f=1.0):
    ## will solve for skew keeping rr and fly from post_s
    ## need to strip post_s and get low_vol for bisection
    rr25 = post_s.rr_25
    rr10 = post_s.rr_10
    fly25 = post_s.fly_25
    fly10 = post_s.fly_10
    vol_low = max(0, rr25/2 - fly25, rr10/2 - fly10, - rr25/2 - fly25,
                  - rr10/2 - fly10) + 0.0025
    vol_high = 10*pre_v
    p_u = 1.0 / (1.0 + up_f)
    p_d = 1.0 - p_u
    s = post_s.spot
    expiry = post_s.expiry
    ird = post_s.ir_d
    irf = post_s.ir_f
    prem_b = bp.bs_str(s, k, pre_v, expiry, ird, irf)
    mid_vol = (vol_low + vol_high) / 2.0
    mid_skew = Skew(s, expiry, ird, irf, mid_vol, rr25, rr10, fly25, fly10)
    epsilon = 0.000000001
    i = 0
    while vol_high - vol_low >= epsilon and i < 100:
        mid_vol = (vol_low + vol_high) / 2.0
        mid_skew = Skew(s, expiry, ird, irf, mid_vol, rr25, rr10, fly25, fly10)
        k_up = k*(1 - egap*up_f)
        k_dn = k*(1 + egap)
        vol_up = mid_skew.get_vol(k_up)
        vol_dn = mid_skew.get_vol(k_dn)
        prem_up = bp.bs_str(s, k_up, vol_up, expiry, ird, irf)
        prem_dn = bp.bs_str(s, k_dn, vol_dn, expiry, ird, irf)
        temp_prem = prem_dn*p_d + prem_up*p_u
        if temp_prem > prem_b:
            vol_high = mid_vol
        else:
            vol_low = mid_vol
        i += 1
    return mid_vol

def gap_vol(k, spot, expiry, ir_d, ir_f, base_v, egap, up_fact=1.0):
    ''' calculates pre vol assuming we know gap and post vol 
    its the inverse of the implied_gap function (curr_vol -> implied_gap) 
    now we have implied_gap -> curr_vol
    '''
    p_u = 1.0 / (1.0 + up_fact)
    p_d = 1.0 - p_u
    prem_after = (bp.bs_str(spot, k*(1 + egap), base_v, expiry, ir_d, ir_f)
                  *p_d +
                  bp.bs_str(spot, k*(1 - egap * up_fact), base_v, expiry,
                            ir_d, ir_f) * p_u)
    return bp.implied_vol_str(prem_after, spot, k, expiry, ir_d , ir_f)

def gap_vol_skew(k, post_skew, egap, up_fact=1.0):
    ''' same as gap_vol, but we have skew of post vol
    '''
    p_u = 1.0 / (1.0 + up_fact)
    p_d = 1.0 - p_u
    spot = post_skew.spot
    expiry = post_skew.expiry
    ir_d = post_skew.ir_d
    ir_f = post_skew.ir_f
    up_gap_k = k*(1 - egap*up_fact)
    down_gap_k = k*(1 + egap)
    up_gap_vol = post_skew.get_vol(up_gap_k)
    down_gap_vol = post_skew.get_vol(down_gap_k)
    prem_after = (bp.bs_str(spot, down_gap_k, down_gap_vol, expiry, ir_d, ir_f)
                  *p_d +
                  bp.bs_str(spot, up_gap_k, up_gap_vol, expiry, ir_d, ir_f)*p_u)
    return bp.implied_vol_str(prem_after, spot, k, expiry, ir_d , ir_f)

####################################################################
##
####################################################################

class Event(object):

    def __init__(self, spot, strike, expiry, curr_vol, base_vol, up_factor=1.0,
                 ir_d = 0.0, ir_f = 0.0):
        self.spot = spot
        self.strike = strike
        self.expiry = expiry
        self.curr_vol = curr_vol
        self.base_vol = base_vol
        self.up_factor = up_factor
        self.ir_d = ir_d
        self.ir_f = ir_f
        self.fwd = spot * bp.df(ir_d,expiry) / bp.df(ir_f,expiry)
        self.imp_gap = self.get_implied_gap()

    def get_implied_gap(self, up_factor=88.8):
        ''' gets gap implied by data used to instantiate the Event object
        '''
        if up_factor == 88.8:
            up_factor = self.up_factor
        temp = implied_gap(self.strike, self.spot, self.expiry, self.ir_d,
                           self.ir_f, self.curr_vol, self.base_vol, up_factor)
        return (temp, temp*up_factor)

    def get_pre_vol(self, gap, up_factor=88.8):
        ''' calculates what pre_vol should be for that gap and data given
        gap is for down move (thats convention for all things in here)
        '''
        if up_factor == 88.8:
            up_factor = self.up_factor
        return gap_vol(self.strike, self.spot, self.expiry, self.ir_d,
                       self.ir_f, self.base_vol, gap, up_factor)

        '''  def post_vol_smile(self, pre_skew, num_k=10, up_factor=88.8, plot=True, over_gap=88.8):
        low_k = self.fwd*(1 - 2*self.curr_vol*sqrt(self.expiry))
        inc = (self.fwd - low_k)/num_k
        strikes = []
        vols = []
        if up_factor == 88.8:
            up_factor = self.up_factor
        for i in range(num_k*2 + 1):
            strikes.append(low_k + inc*i)
        if over_gap == 88.8:
            strike_gap = implied_gap(self.strike, self.spot, self.expiry,
                                     self.ir_d, self.ir_f, self.curr_vol,
                                     self.base_vol, up_factor)
        else:
            strike_gap = over_gap
        for j in strikes: '''
        

    def pre_vol_smile(self, num_k=10, up_factor=88.8, plot=True, over_gap=88.8):
        ''' takes strike w/ its pre and post vols used to create Event
        object calculates implied gap for that strike, and uses to build
        whole smile
        '''
        low_k = self.fwd*(1 - 2*self.curr_vol*sqrt(self.expiry))
        inc = (self.fwd - low_k)/num_k
        strikes = []
        vols = []
        if up_factor == 88.8:
            up_factor = self.up_factor
        for i in range(num_k*2 + 1):
            strikes.append(low_k + inc*i)
        if over_gap == 88.8:
            strike_gap = implied_gap(self.strike, self.spot, self.expiry,
                                     self.ir_d, self.ir_f, self.curr_vol,
                                     self.base_vol, up_factor)
        else:
            strike_gap = over_gap
        for j in strikes:
            vols.append(gap_vol(j, self.spot, self.expiry, self.ir_d, self.ir_f,
                                self.base_vol, strike_gap, up_factor))
        if plot:
            minx = min(strikes)*0.99
            maxx = max(strikes)*1.01
            miny = min(vols)*0.975
            maxy = max(vols)*1.025
            upmove = self.fwd*(1 + strike_gap*up_factor)
            dwnmove = self.fwd*(1 - strike_gap)
            plt.scatter(strikes, vols, alpha = 0.7)
            plt.plot([self.fwd, self.fwd], [miny, maxy], 'k--', alpha=0.6,
                     linewidth=1.5)
            plt.plot([upmove, upmove], [miny, maxy], 'r--', alpha=0.6,
                     linewidth=1.5)
            plt.plot([dwnmove, dwnmove], [miny, maxy], 'r--', alpha=0.6,
                     linewidth=1.5)
            plt.axis([minx, maxx, miny, maxy])
            plt.grid(True)
            plt.show()
        return (strikes, vols)

    def gap_smile(self, num_k=10, plot=True):
        ''' assumes all strikes have same pre and post vol, calculates
        implied gap simplest model, not what you want to use
        '''
        low_k = self.fwd*(1 - self.curr_vol*2.0*sqrt(self.expiry))
        inc = (self.fwd - low_k)/num_k
        strikes = []
        e_gap = []
        for i in range(num_k*2 + 1):
            strikes.append(low_k + inc*i)
        for j in strikes:
            e_gap.append(implied_gap(j, self.spot, self.expiry, self.ir_d,
                                     self.ir_f, self.curr_vol, self.base_vol,
                                     self.up_factor))
        if plot:
            minx = min(strikes)*0.99
            maxx = max(strikes)*1.01
            miny = min(e_gap)*0.95
            maxy = max(e_gap)*1.05
            plt.scatter(strikes, e_gap, alpha=0.7)
            plt.plot([self.fwd, self.fwd], [miny, maxy], 'k--', alpha=0.6,
                     linewidth=1.5)
            plt.grid(True)
            plt.axis([minx, maxx, miny, maxy])
            plt.show()
        return (strikes, e_gap)
    
    def compare_factor(self, up_factor, num_k=10):
        ''' take in an array of different factors
        '''
        num_f = len(up_factor)
        ymin = 100
        ymax = 0
        colors = ['blue', 'grey', 'red', 'black', 'green', 'blue', 'grey',
                  'red', 'black', 'green']
        for i in range(num_f):
            temp = self.pre_vol_smile(num_k, up_factor[i], False)
            lab1 = 'factor: %.2f'%(up_factor[i])
            plt.scatter(temp[0], temp[1], c=colors[i], edgecolor=colors[i],
                        alpha=0.7, label=lab1)
            ymin = min(ymin, min(temp[1]))
            ymax = max(ymax, max(temp[1]))
        xmin = min(temp[0])*0.99
        xmax = max(temp[0])*1.01
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4,
                   mode="expand", borderaxespad=0.)
        plt.plot([self.fwd, self.fwd], [0.95*ymin, 1.05*ymax], 'k--',
                 alpha=0.6, linewidth=1.5)
        plt.grid(True)
        plt.axis([xmin, xmax, ymin*0.95, ymax*1.05])
        plt.show()
        return True

    def __str__(self):
        params = 'input data\nspot:\t%.4f\nfwd:\t%.4f\nstrike: %.4f\n' \
                 %(self.spot, self.fwd, self.strike)
        params += 'ir dom:\t%.2f%%\tir for:\t%.2f%%\n' \
                  %(self.ir_d*100, self.ir_f*100)
        params += 'prevol: %.2f%%\tpostvol: %.2f%%\nexpiry (days):\t%.1f\n' \
                  %(self.curr_vol*100, self.base_vol*100, 365.0*self.expiry)
        params += 'up factor:\t%.2f\n' %(self.up_factor)
        p_u = 1.0 / (1.0 + self.up_factor)
        p_d = 1.0 - p_u
        em = 2*self.up_factor*self.imp_gap[0]/(1 + self.up_factor)
        move = 'expected move:\t%.4f%%\nmove up:\t%.4f%%  w/p  %.2f%%\n' \
               %(em*100, self.imp_gap[1]*100, p_u*100)
        move += 'move down:\t%.4f%%  w/p  %.2f%%'\
               %(self.imp_gap[0]*100, p_d*100)
        return params+'\n'+move
    
####################################################################
##
####################################################################
    
class Event_Skew(object):

    def __init__(self, strike, curr_vol, post_skew, up_factor=1.0):
        self.spot = post_skew.spot
        self.strike = strike
        self.expiry = post_skew.expiry
        self.curr_vol = curr_vol
        self.post_skew = post_skew
        self.up_factor = up_factor
        self.ir_d = post_skew.ir_d
        self.ir_f = post_skew.ir_f
        self.fwd = self.spot * bp.df(self.ir_d, self.expiry) / \
                   bp.df(self.ir_f, self.expiry)
        self.imp_gap = self.get_implied_gap()

    def get_implied_gap(self, up_factor=88.8):
        ' gets gap implied by data used to instantiate the Event object'
        if up_factor == 88.8:
            up_factor = self.up_factor
        temp = implied_gap_skew(self.strike, self.curr_vol, self.post_skew,
                                up_factor)
        return (temp, temp*up_factor)

    def get_pre_vol(self, gap, up_factor=88.8):
        ''' calculates what pre_vol shouldbe for that gap and data given
        gap is for down move (thats convention for all things in here)
        '''
        if up_factor == 88.8:
            up_factor = self.up_factor
        return gap_vol_skew(self.strike, self.post_skew, gap, up_factor)

    def pre_vol_smile(self, num_k=10, up_factor=88.8, plot=True, over_gap=88.8):
        ''' takes strike w/ its pre and post vols used to create Event
        object calculates implied gap for that strike, and uses to build
        whole smile
        '''
        low_k = self.fwd*(1 - 2*self.curr_vol*sqrt(self.expiry))
        inc = (self.fwd - low_k)/num_k
        strikes = []
        vols = []
        if up_factor == 88.8:
            up_factor = self.up_factor
        for i in range(num_k*2 + 1):
            strikes.append(low_k + inc*i)
        if over_gap == 88.8:
            strike_gap = implied_gap_skew(self.strike, self.curr_vol,
                                          self.post_skew, up_factor)
        else:
            strike_gap = over_gap
        for j in strikes:
            vols.append(gap_vol_skew(j, self.post_skew, strike_gap, up_factor))
        if plot:
            minx = min(strikes)*0.99
            maxx = max(strikes)*1.01
            miny = min(vols)*0.975
            maxy = max(vols)*1.025
            upmove = self.fwd*(1 + strike_gap*up_factor)
            dwnmove = self.fwd*(1 - strike_gap)
            plt.scatter(strikes, vols, alpha=0.7)
            plt.plot([self.fwd, self.fwd], [miny, maxy], 'k--', alpha=0.6,
                     linewidth=1.5)
            plt.plot([upmove, upmove], [miny, maxy], 'r--', alpha=0.6,
                     linewidth=1.5)
            plt.plot([dwnmove, dwnmove], [miny, maxy], 'r--', alpha=0.6,
                     linewidth=1.5)
            plt.axis([minx, maxx, miny, maxy])
            plt.grid(True)
            plt.show()
        return (strikes, vols)

    def gap_smile(self, num_k=10, plot=True):
        ''' assumes all strikes have same pre and post vol, calculates
        implied gap simplest model, not what you want to use
        '''
        low_k = self.fwd*(1 - self.curr_vol*2.0*sqrt(self.expiry))
        inc = (self.fwd - low_k)/num_k
        strikes = []
        e_gap = []
        for i in range(num_k*2 + 1):
            strikes.append(low_k + inc*i)
        for j in strikes:
            e_gap.append(implied_gap_skew(j, self.curr_vol, self.post_skew,
                                          self.up_factor))
        if plot:
            minx = min(strikes)*0.99
            maxx = max(strikes)*1.01
            miny = min(e_gap)*0.95
            maxy = max(e_gap)*1.05
            plt.scatter(strikes, e_gap, alpha=0.7)
            plt.plot([self.fwd, self.fwd], [miny, maxy], 'k--', alpha=0.6,
                     linewidth=1.5)
            plt.grid(True)
            plt.axis([minx, maxx, miny, maxy])
            plt.show()
        return (strikes, e_gap)
    
    def compare_factor(self, up_factor, num_k=10):
        ' take in an array of different factors'
        num_f = len(up_factor)
        ymin = 100
        ymax = 0
        colors = ['blue', 'grey', 'red', 'black', 'green', 'blue', 'grey',
                  'red', 'black', 'green']
        for i in range(num_f):
            temp = self.pre_vol_smile(num_k, up_factor[i], False)
            lab1 = 'factor: %.2f'%(up_factor[i])
            plt.scatter(temp[0], temp[1], c=colors[i], edgecolor=colors[i],
                        alpha=0.7, label=lab1)
            ymin = min(ymin, min(temp[1]))
            ymax = max(ymax, max(temp[1]))
        xmin = min(temp[0])*0.99
        xmax = max(temp[0])*1.01
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4,
                   mode="expand", borderaxespad=0.)
        plt.plot([self.fwd, self.fwd], [0.95*ymin, 1.05*ymax], 'k--',
                 alpha=0.6, linewidth=1.5)
        plt.grid(True)
        plt.axis([xmin, xmax, ymin*0.95, ymax*1.05])
        plt.show()
        return True

    def __str__(self):
        params = 'input data\nspot:\t%.4f\nfwd:\t%.4f\nstrike: %.4f\n' \
                 %(self.spot, self.fwd, self.strike)
        params += 'ir dom:\t%.2f%%\tir for:\t%.2f%%\n' \
                  %(self.ir_d*100, self.ir_f*100)
        params += 'prevol: %.2f%%\tpostvol: %.2f%%\nexpiry (days):\t%.1f\n' \
                  %(self.curr_vol*100, self.post_skew.get_vol(self.strike)*100,
                    365.0*self.expiry)
        params += 'up factor:\t%.2f\n' %(self.up_factor)
        p_u = 1.0 / (1.0 + self.up_factor)
        p_d = 1.0 - p_u
        em = 2*self.up_factor*self.imp_gap[0]/(1 + self.up_factor)
        move = 'expected move:\t%.4f%%\nmove up:\t%.4f%%  w/p  %.2f%%\n' \
               %(em*100, self.imp_gap[1]*100, p_u*100)
        move += 'move down:\t%.4f%%  w/p  %.2f%%'\
               %(self.imp_gap[0]*100, p_d*100)
        return params+'\n'+move

