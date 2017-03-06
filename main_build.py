#!/usr/bin/env python3
import gap_event_smile as ges
from Vol_Market import Vol_mkt

# load postvol market run
def file_run(filename):
    f_in = open(filename, 'rU')
    f_in.readline()
    expiry = []
    atmf = []
    rr25 = []
    rr10 = []
    fly25 = []
    fly10 = []
    ird = []
    irf = []
    for line in f_in:
        temp = line.split()
        expiry.append(float(temp[0]))
        atmf.append(float(temp[1]))
        rr25.append(float(temp[2]))
        rr10.append(float(temp[3]))
        fly25.append(float(temp[4]))
        fly10.append(float(temp[5]))
        ird.append(float(temp[6]))
        irf.append(float(temp[7]))
    f_in.close()
    # adding spot manually
    vm = Vol_mkt(10, expiry, atmf, rr25, rr10, fly25, fly10, ird, irf)
    return vm

def main():
    # load postvol run from file
    filename = 'opt_run.txt'
    postvol_run = file_run(filename)
    num_curves = len(postvol_run.expiry)
    # mkt info for data 
    s = 10
    k = 10
    expiry = 2/365.0
    pre_v = 0.15
    ird = 0.0
    irf = 0.0
    up_f = 1/2.0
    # skew
    rr_25 = 1.0/100
    rr_10 = 2.0/100
    fly_25 = 0.25/100
    fly_10 = 1.0/100
    
    # gets post data for specific date  and strike from run
    pv_skew = postvol_run.interp_skew(expiry)
    postv_k = pv_skew.get_vol(k)
    print(postv_k)
    '''
    # build event
    ev = ges.Event(k, pre_v, pv_skew, up_f)
    ig = ev.get_implied_gap()
    
    # build all prevol curves
    for i in range(num_curves):
        expiry = postvol_run.expiry[i]
        pv_skew = postvol_run.interp_skew(expiry)
        pre_atmf = ges.pre_vol(k, pv_skew, ig[0], up_f)
        temp_ev = ges.Event(k, pre_atmf, pv_skew, up_f)
        print('\n\n------------------------------------\n')
        print(temp_ev)
        temp_ev.pre_vol_smile()
    '''
if __name__ == '__main__':
    main()
