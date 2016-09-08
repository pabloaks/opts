import gap_event_uneven as geu
import gap_event as ge

def main():
    ## market data
    s = 10.00
    k = 10.00
    expiry = 1/365
    ird = 0.0
    irf = 0.0
    pre_v = 0.15
    up_f = 1/2.0
    post_up = 0.10
    post_dn = 0.14

    # functions
    # test implied gap
    print('uneven')
    ig = geu.implied_gap(k, s, expiry, ird, irf, pre_v, post_up, post_dn, up_f)
    print('impgap: %.3f%%'%(100*ig))
    print('vs. original')
    ig_o = ge.implied_gap(k, s, expiry, ird, irf, pre_v, post_up, up_f)
    print('impgap: %.3f%%'%(100*ig_o))

    # test postvol
    print('\n\npostvol\noriginal')
    postv_o = ge.post_vol(k, s, expiry, ird, irf, pre_v, ig_o, up_f)
    print('post orig: %.2f%%'%(100*postv_o))
    print('volfactor')
    postv = geu.post_vol(k, s, expiry, ird, irf, pre_v, ig, 1/1.4, up_f)
    print('postv: %.2f%%'%(100*postv))

    # test prevol
    print('\n\npretvol\noriginal')
    prev_o = ge.pre_vol(k, s, expiry, ird, irf, post_up, ig_o, up_f)
    print('prev orig: %.2f%%'%(100*prev_o))
    print('vs. uneven')
    prev = geu.pre_vol(k, s, expiry, ird, irf, post_up, post_dn, ig, up_f)
    print('prev: %.2f%%'%(100*prev))

##    # objects
##    print('\n\n\nObject\n')
##    ev = geu.Event(s, k, expiry, pre_v, post_up, post_dn, up_f, ird, irf)
##    ev_o = ge.Event(s, k, expiry, pre_v, post_up, up_f, ird, irf)
##    # implied gap
##    ig = ev.get_implied_gap()
##    print('unevengap: %.3f%%'%(100*ig[0]))
##
##    # prevol run
##    sk = ev.prevol_run()
##    #print(sk)
##    sk_o = ev_o.prevol_run()
##    #print('\n\n')
##    #print(sk_o)
##    # prevol method
##    prev = ev.get_pre_vol(ig[0])
##    print('prev: %.2f%%'%(100*prev))
##    
##    
##    
##    
    

if __name__ == '__main__':
    main()
