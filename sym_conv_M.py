#%%
import sympy as sym
import numpy as np


# Symbols for converter voltages (V), angles (theta), and modules (absV)
V_f, V_c, V_g = sym.symbols('V_f V_c V_g', real=True)
t_f, t_c, t_g = sym.symbols('t_f t_c t_g', real=True)
gkm,bkm,gmm, bmm = sym.symbols('g_{km} b_{km} g_{mm} b_{mm}', real=True)


V_dc = sym.symbols('V_dc', real=True)


#%%

#%%
M= V_g/V_dc


M_dVg=sym.diff(M, V_g)
M_dVdc=sym.diff(M, V_dc)
# %%
