#%%
import sympy as sym
import numpy as np


# Symbols for converter voltages (V), angles (theta), and modules (absV)
V_f, V_c, V_g = sym.symbols('V_f V_c V_g', real=True)
t_f, t_c, t_g = sym.symbols('t_f t_c t_g', real=True)

cV_f=V_f*sym.exp(1j*t_f)
cV_c=V_c*sym.exp(1j*t_c)
cV_g=V_g*sym.exp(1j*t_g)

z=0.01+0.01j
bsh=0.01j
#%%
ybr=1/z
If_g=(cV_f-cV_g)*ybr
If_c=(cV_f-cV_c)*ybr
Ish=cV_f*bsh

If_re=sym.re(sym.simplify(If_g+If_c+Ish))
If_im=sym.im(sym.simplify(If_g+If_c+Ish))
Ish_re=sym.re(sym.simplify(Ish))
Ish_im=sym.im(sym.simplify(Ish))
#%%
dIsh_re_dt=sym.diff(Ish_re,t_f)
dIsh_re_dv=sym.diff(Ish_re,V_f)
dIsh_im_dt=sym.diff(Ish_im,t_f)
dIsh_im_dv=sym.diff(Ish_im,V_f)

#%%

dIfre_dVf=sym.diff(If_re,V_f)
dIfim_dVf=sym.diff(If_im,V_f)
dIfre_dtf=sym.diff(If_re,t_f)
dIfim_dtf=sym.diff(If_im,t_f)

dIfre_dVc=sym.diff(If_re,V_c)
dIfim_dVc=sym.diff(If_im,V_c)
dIfre_dtc=sym.diff(If_re,t_c)
dIfim_dtc=sym.diff(If_im,t_c)


dIfre_dVg=sym.diff(If_re,V_g)
dIfim_dVg=sym.diff(If_im,V_g)
dIfre_dtg=sym.diff(If_re,t_g)
dIfim_dtg=sym.diff(If_im,t_g)

# %%
vf=1
vc=1
vg=1
tf=45*np.pi/180
tc=45*np.pi/180
tg=45*np.pi/180


dIfre_dVf.subs({V_f:vf,V_c:vc,V_g:vg,t_f:tf,t_c:tc,t_g:tg})
dIfim_dVf.subs({V_f:vf,V_c:vc,V_g:vg,t_f:tf,t_c:tc,t_g:tg})
dIfre_dtf.subs({V_f:vf,V_c:vc,V_g:vg,t_f:tf,t_c:tc,t_g:tg})
dIfim_dtf.subs({V_f:vf,V_c:vc,V_g:vg,t_f:tf,t_c:tc,t_g:tg})
dIfre_dVc.subs({V_f:vf,V_c:vc,V_g:vg,t_f:tf,t_c:tc,t_g:tg})
dIfim_dVc.subs({V_f:vf,V_c:vc,V_g:vg,t_f:tf,t_c:tc,t_g:tg})
dIfre_dtc.subs({V_f:vf,V_c:vc,V_g:vg,t_f:tf,t_c:tc,t_g:tg}) 
dIfim_dtc.subs({V_f:vf,V_c:vc,V_g:vg,t_f:tf,t_c:tc,t_g:tg})
dIfre_dVg.subs({V_f:vf,V_c:vc,V_g:vg,t_f:tf,t_c:tc,t_g:tg})
dIfim_dVg.subs({V_f:vf,V_c:vc,V_g:vg,t_f:tf,t_c:tc,t_g:tg})
dIfre_dtg.subs({V_f:vf,V_c:vc,V_g:vg,t_f:tf,t_c:tc,t_g:tg})
dIfim_dtg.subs({V_f:vf,V_c:vc,V_g:vg,t_f:tf,t_c:tc,t_g:tg})
#%%