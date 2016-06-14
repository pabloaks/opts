from math import *
import random

def phi(x):
    a1 =  0.254829592; a2 = -0.284496736; a3 =  1.421413741
    a4 = -1.453152027; a5 =  1.061405429; p  =  0.3275911

    sign = 1
    if x < 0:
        sign = -1
    x = abs(x)/sqrt(2.0)
    t = 1.0 / (1.0 + p*x)
    y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t*exp(-x*x)
    return 0.5*(1.0 + sign*y)

def norm_CDF_inv(p):
    c = [2.515517, 0.802853, 0.010328]
    d = [1.432788, 0.189269, 0.001308]
    if p < 0.5:
        t = sqrt(-2.0*log(p))
        t = t - ((c[2]*t + c[1])*t + c[0]) / (((d[2]*t + d[1])*t + d[0])*t + 1.0)
        return -t
    else:
        t = sqrt(-2.0*log(1-p))
        t = t - ((c[2]*t + c[1])*t + c[0]) / (((d[2]*t + d[1])*t + d[0])*t + 1.0)
        return t
        
def rand_sim(spot,vol,start,end, num):
    prices = [spot]
    for i in range(0,num):
        prices.append(prices[i]*(1+norm_CDF_inv(random.random())*vol*sqrt((start-end)/num)))
    return prices
   

print('hi')

