#%%
import pandas as pd
import matplotlib.pyplot as plt


file="SE_data/"
dfres=pd.read_csv(file+"state_IEEE14_rakp2009x1SemMedidasloadvar.csv")
# %%



val=dfres[(dfres["de"]==4)&(dfres["tipo"]=="v")&(dfres["sample"]==0)&(dfres["method"]=="MAP_SCADA")]["error"].values
# %%


plt.plot(val)

# %%
