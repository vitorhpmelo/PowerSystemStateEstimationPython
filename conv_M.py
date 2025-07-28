#%%
import sympy as sym
import numpy as np


# Symbols for converter voltages (V), angles (theta), and modules (absV)
V_f, V_c, V_g = sym.symbols('V_f V_c V_g', real=True)
t_f, t_c, t_g = sym.symbols('t_f t_c t_g', real=True)

V_dc = sym.symbols('V_dc', real=True)




cV_f = V_f * sym.exp(1j * t_f)
cV_c = V_c * sym.exp(1j * t_c)
cV_g = V_g * sym.exp(1j * t_g)  

M= V_g/V_dc


M_dVg=sym.diff(M, V_g)
M_dVdc=sym.diff(M, V_dc)
# %%
