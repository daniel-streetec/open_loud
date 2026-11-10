"""Own normalized biquad implementation of bilinear LP/HP formulae.
Reference: W3C Audio EQ Cookbook, 2021-06-08, https://www.w3.org/TR/audio-eq-cookbook/
Coefficients use y=b0*x+b1*x1+b2*x2-a1*y1-a2*y2. No DSP firmware format implied.
"""
import math,cmath
def biquad(kind,fc,fs,q):
    assert kind in ('lp','hp') and 0<fc<fs/2 and q>0
    w=2*math.pi*fc/fs;c=math.cos(w);alpha=math.sin(w)/(2*q)
    if kind=='lp':b=[(1-c)/2,1-c,(1-c)/2]
    else:b=[(1+c)/2,-(1+c),(1+c)/2]
    a0=1+alpha
    return dict(b=[v/a0 for v in b],a=[1,-2*c/a0,(1-alpha)/a0])
def response(section,f,fs):
    z=cmath.exp(-2j*math.pi*f/fs);b=section['b'];a=section['a']
    return (b[0]+b[1]*z+b[2]*z*z)/(1+a[1]*z+a[2]*z*z)
def cascade(sections,f,fs):
    result=1+0j
    for s in sections:result*=response(s,f,fs)
    return result
def lr4(kind,fc,fs):return [biquad(kind,fc,fs,1/math.sqrt(2)) for _ in range(2)]
def butterworth4_highpass(fc,fs):
    return [biquad('hp',fc,fs,1/(2*math.cos(math.pi/8))),biquad('hp',fc,fs,1/(2*math.cos(3*math.pi/8)))]
