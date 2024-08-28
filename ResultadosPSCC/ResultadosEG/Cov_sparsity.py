
#%%
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np


dsys={"IEEE14":"14 bus"}
colors=["#D6870D","#099358","#D60D0D","#291C95"]

dfDATA={}

Cov_cmed=np.loadtxt("covComMedidas_idx_0_Cov.csv",dtype=float)
#%%

Cov_smed=np.loadtxt("covSemMedidas_idx_0_Cov.csv",dtype=float)


# %%


Cov_Original=np.loadtxt("covSemMedidas_idx_Original_Cov.csv",dtype=float)

#%%

Cov_cmed=np.abs(Cov_cmed)

Cov_smed=np.abs(Cov_smed)

Cov_Original=np.abs(Cov_Original)
#%%

k=0.55
fig, ax =plt.subplots(ncols=3,nrows=1,figsize=(k*16,k*6))


ax[0].spy(Cov_Original,precision=1e-18)

ax[1].spy(Cov_smed,precision=1e-18)

ax[2].spy(Cov_cmed,precision=1e-18)





#%%