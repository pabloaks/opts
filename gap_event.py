from opts import basic_pricer as bp
from math import *
import matplotlib.pyplot as plt
#import Vol_Market

def implied_gap(k, s, expiry, ird, irf, pre_v, post_v, up_f=1.0):
    ''' will bump the strike by the event gap, instead of the spot, this
    way there is no need to worry about the currency of the p/l, since
    spot is not moving, need to think about this about more but otherwise
    results seems off, too uneven 
    up factor = magnitude move up / magnitude move down
    returns magnitude of move down
    '''
    p_u = 1.0 / (1.0 + up_f)
    p_d = 1.0 - p_u
    curr_prem = bp.bs_str(s, k, pre_v, expiry, ird, irf)
    gap_low = 0.0
    gap_high = pre_v*sqrt(3.0*expiry/pi)*1.1*max(1,1.0/up_f)
    ## for low strikes can potentially pass a -ve strike in bs_str()
    ## for very high up_factor, so need to be careful,
    ## and way to control it is with gap_high /// (looks ok now)
    mid_gap = (gap_low + gap_high) / 2.0
    epsilon = 0.000000001
    i = 0
    while gap_high - gap_low >= epsilon and i < 100:
        mid_gap = (gap_low + gap_high) / 2.0
        prem_dn = bp.bs_str(s, k*(1 + mid_gap), post_v, expiry, ird, irf)
        prem_up = bp.bs_str(s, k*(1 - mid_gap*up_f), post_v, expiry, ird, irf)
        temp_prem = prem_dn*p_d + prem_up*p_u
        if temp_prem > curr_prem:
            gap_high = mid_gap
        else:
            gap_low = mid_gap
        i += 1
    return mid_gap

## use with care, for large gaps there is noise
def post_vol(k, s, expiry, ird, irf, pre_v, egap, up_f=1.0):
    ''' calculates post vol
    '''
    ## not sure temp_prem is monotonic fn of vol
    ## for big gaps post_vol doesnt always match
    ## unstable solutions so get some errors
    ## need to add check for prem(pre_v) > gap
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
        prem_up = bp.bs_str(s, k*(1 - egap*up_f), mid_vol, expiry, ird, irf)
        temp_prem =  prem_dn*p_d + prem_up*p_u
        if temp_prem > prem_b:
            vol_high = mid_vol
        else:
            vol_low = mid_vol
        i += 1
    return mid_vol

def pre_vol(k, s, expiry, ird, irf, post_v, egap, up_f=1.0):
    ''' calculates pre vol assuming we know gap and post vol 
    its the inverse of the implied_gap function (curr_vol -> implied_gap) 
    now we have implied_gap -> curr_vol
    '''
    p_u = 1.0 / (1.0 + up_f)
    p_d = 1.0 - p_u
    prem_dn = bp.bs_str(s, k*(1 + egap), post_v, expiry, ird, irf)
    prem_up = bp.bs_str(s, k*(1 - egap*up_f), post_v, expiry, ird, irf)
    prem_after = prem_dn*p_d + prem_up*p_u
    return bp.implied_vol_str(prem_after, s, k, expiry, ird , irf)

''' *********************************************************************
********************************************************************* '''
class Event(object):

    def __init__(self, s, k, expiry, pre_vol, post_vol, up_f=1.0, ird=0.0,
                 irf=0.0):
        self.s = s
        self.k = k
        self.expiry = expiry
        self.pre_vol = pre_vol
        self.post_vol = post_vol
        self.up_f = up_f
        self.ird = ird
        self.irf = irf
        self.fwd = s * bp.df(ird, expiry) / bp.df(irf, expiry)
        self.imp_gap = self.get_implied_gap()

    def get_implied_gap(self, up_f=88.8):
        ' gets gap implied by data used to instantiate the Event object'
        if up_f == 88.8:
            up_f = self.up_f
        temp = implied_gap(self.k, self.s, self.expiry, self.ird, self.irf,
                           self.pre_vol, self.post_vol, up_f)
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
        pre_skew = Vol_Market.Skew(self.s, self.expiry, self.ird, self.irf,
                                   atmf, rr25, rr10, fly25, fly10)
        return pre_skew

    def get_pre_vol_k(self, k):
        ' returns the pre vol for input strike '
        return pre_vol(k, self.s, self.expiry, self.ird, self.irf,
                       self.post_vol, self.imp_gap[0], self.up_f)

    def get_pre_vol(self, gap, up_f=88.8):
        ''' calculates what pre_vol should be for that gap and data given
        gap is for down move (thats convention for all things in here)
        '''
        if up_f == 88.8:
            up_f = self.up_f
        return pre_vol(self.k, self.s, self.expiry, self.ird, self.irf,
                       self.post_vol, gap, up_f)

    def get_post_vol(self, gap, up_f=88.8):
        ' override gap and (up_f) to calculate new postvol'
        if up_f == 88.8:
            up_f = self.up_f
        return post_vol(self.k, self.s, self.expiry, self.ird, self.irf,
                        self.pre_vol, gap, up_f)

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

    def post_vol_smile(self, num_k=10, up_f=88.8, plot=True, over_gap=88.8):
        low_k = self.fwd*(1 - 2*self.pre_vol*sqrt(self.expiry))
        inc = (self.fwd - low_k)/num_k
        strikes = []
        vols = []
        if up_f == 88.8:
            up_f = self.up_f
        for i in range(num_k*2 + 1):
            strikes.append(low_k + inc*i)
        if over_gap == 88.8:
            strike_gap = implied_gap(self.k, self.s, self.expiry, self.ird,
                                     self.irf, self.pre_vol, self.post_vol,
                                     up_f)
        else:
            strike_gap = over_gap
        for j in strikes:
            vols.append(post_vol(j, self.s, self.expiry, self.ird,
                                 self.irf, self.pre_vol, strike_gap, up_f))
        if plot:
            minx = min(strikes)*0.99
            maxx = max(strikes)*1.01
            miny = min(vols)*0.975
            maxy = max(vols)*1.025
            upmove = self.fwd*(1 + strike_gap*up_f)
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
                        

    def pre_vol_smile(self, num_k=10, up_f=88.8, plot=True, over_gap=88.8):
        ''' takes strike w/ its pre and post vols used to create Event
        object calculates implied gap for that strike, and uses to build
        whole smile
        '''
        low_k = self.fwd*(1 - 2*self.pre_vol*sqrt(self.expiry))
        inc = (self.fwd - low_k)/num_k
        strikes = []
        vols = []
        if up_f == 88.8:
            up_f = self.up_f
        for i in range(num_k*2 + 1):
            strikes.append(low_k + inc*i)
        if over_gap == 88.8:
            strike_gap = implied_gap(self.k, self.s, self.expiry, self.ird,
                                     self.irf, self.pre_vol, self.post_vol,
                                     up_f)
        else:
            strike_gap = over_gap
        for j in strikes:
            vols.append(pre_vol(j, self.s, self.expiry, self.ird, self.irf,
                                self.post_vol, strike_gap, up_f))
        if plot:
            minx = min(strikes)*0.99
            maxx = max(strikes)*1.01
            miny = min(vols)*0.975
            maxy = max(vols)*1.025
            upmove = self.fwd*(1 + strike_gap*up_f)
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

    def naive_gap_smile(self, num_k=10, plot=True):
        ''' assumes all strikes have same pre and post vol, calculates
        implied gap. simplest model, not what you want to use
        '''
        low_k = self.fwd*(1 - self.pre_vol*2.0*sqrt(self.expiry))
        inc = (self.fwd - low_k)/num_k
        strikes = []
        e_gap = []
        for i in range(num_k*2 + 1):
            strikes.append(low_k + inc*i)
        for j in strikes:
            e_gap.append(implied_gap(j, self.s, self.expiry, self.ird, self.irf,
                                     self.pre_vol, self.post_vol, self.up_f))
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
    
    def compare_factor(self, up_f, num_k=10):
        ''' take in an array of different factors
        '''
        num_f = len(up_f)
        ymin = 100
        ymax = 0
        colors = ['blue', 'grey', 'red', 'black', 'green', 'blue', 'grey',
                  'red', 'black', 'green']
        for i in range(num_f):
            temp = self.pre_vol_smile(num_k, up_f[i], False)
            lab1 = 'factor: %.2f'%(up_f[i])
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
                 %(self.s, self.fwd, self.k)
        params += 'ir dom:\t%.2f%%\tir for:\t%.2f%%\n' \
                  %(self.ird*100, self.irf*100)
        params += 'prevol: %.2f%%\tpostvol: %.2f%%\nexpiry (days):\t%.1f\n' \
                  %(self.pre_vol*100, self.post_vol*100, 365.0*self.expiry)
        params += 'up factor:\t%.2f\n' %(self.up_f)
        p_u = 1.0 / (1.0 + self.up_f)
        p_d = 1.0 - p_u
        em = 2*self.up_f*self.imp_gap[0]/(1 + self.up_f)
        move = 'expected move:\t%.4f%%\nmove up:\t%.4f%%  w/p  %.2f%%\n' \
               %(em*100, self.imp_gap[1]*100, p_u*100)
        move += 'move down:\t%.4f%%  w/p  %.2f%%'\
               %(self.imp_gap[0]*100, p_d*100)
        return params+'\n'+move
