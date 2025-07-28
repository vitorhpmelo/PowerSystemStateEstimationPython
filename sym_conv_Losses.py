#%%
import sympy as sym
import numpy as np


# Symbols for converter voltages (V), angles (theta), and modules (absV)
V_f, V_c, V_g = sym.symbols('V_f V_c V_g', real=True)
t_f, t_c, t_g = sym.symbols('t_f t_c t_g', real=True)
gkm,bkm,gmm, bmm, r = sym.symbols('g_{km} b_{km} g_{mm} b_{mm} R', real=True)
a,b,c= sym.symbols("a b c",real=True)


V_dck,V_dcm = sym.symbols('V_dck V_dcm', real=True)







cV_f = V_f * sym.exp(1j * t_f)
cV_c = V_c * sym.exp(1j * t_c)
cV_g = V_g * sym.exp(1j * t_g)  


cIconv= cV_c*(gmm + 1j*bmm) + cV_f*(gkm + 1j*bkm) 

Pac=sym.re(sym.sympify(cV_c*sym.conjugate(cIconv)))


Pdc=V_dck*2*(V_dck-V_dcm)/r




Iconv_re = sym.sympify(sym.re(cIconv))
Iconv_im = sym.sympify(sym.im(cIconv))
Iconv = sym.sqrt(Iconv_re**2 + Iconv_im**2)
#%%

Ploss= a+b*Iconv+c*Iconv**2


#%%
cons=Ploss+Pac+Pdc

Gkm=-50
Bkm=50

Gmm=50
Bmm=-50

R=0.052

A=0.01103
B=0.0014843759094817334
C=0.0008079535111671217

cons=cons.subs([(gkm,Gkm),(bkm,Bkm),(gmm,Gmm),(bmm,Bmm),(r,R),(a,A),(b,B),(c,C)])

# %%

vdck=1.014783
vdcm=1

Vc=0.9799089641400777
tc=-0.07244342597026035
Vf= 0.990002020199959
tf=-0.07048283677587633
dcons_dVc = sym.diff(cons,V_c)
dcons_dtc = sym.diff(cons,t_c)
dcons_dVf = sym.diff(cons, V_f)
dcons_dtf = sym.diff(cons, t_f)
dcons_dVdck = sym.diff(cons, V_dck)
dcons_dVdcm = sym.diff(cons, V_dcm)


# %%
sublist = [
    (V_dck, vdck),
    (V_dcm, vdcm),
    (V_c, Vc),
    (t_c, tc),
    (V_f, Vf),
    (t_f, tf)
]
print("dcons_dVdck:", dcons_dVdck.subs(sublist))
print("dcons_dVdcm:", dcons_dVdcm.subs(sublist))
print("dcons_dVc:", dcons_dVc.subs(sublist))
print("dcons_dtc:", dcons_dtc.subs(sublist))
print("dcons_dVf:", dcons_dVf.subs(sublist))
print("dcons_dtf:", dcons_dtf.subs(sublist))
# %%
