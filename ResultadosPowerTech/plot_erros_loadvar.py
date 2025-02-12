#%%
import pandas as pd
import matplotlib.pyplot as plt

dfV=pd.read_csv("errosV_compilados4.csv")
dfteta=pd.read_csv("errosteta_compilados4.csv")
dfFACTS=pd.read_csv("errosFACTS_compilados4.csv")
#%%


fig, ax = plt.subplots(nrows=1,ncols=3,figsize=(16,6))

ax[0].set_xlabel("tempo (s)")
ax[0].set_ylabel("MAE")

ax[0].set_title("V")

ax[0].semilogy(dfV.index/10,dfV.WLS.values,label="WLS",ls=":")
ax[0].semilogy(dfV.index/10,dfV.MAP_PMU.values,label="MAP PMU",ls=":")
# ax[0].semilogy(dfV.index/10,dfV.MAP_SCADA.values,label="MAP SCADA")

ax[1].set_xlabel("tempo (s)")
ax[1].set_ylabel("MAE")

ax[1].set_title(r"$\theta$")
ax[1].semilogy(dfteta.index/10,dfteta.WLS,label="WLS",ls=":")
ax[1].semilogy(dfteta.index/10,dfteta.MAP_PMU,label="MAP PMU",ls=":")
# ax[1].semilogy(dfteta.index/100,dfteta.MAP_SCADA,label="MAP SCADA")

ax[2].set_xlabel("tempo (s)")
ax[2].set_ylabel("MAE")
ax[2].set_title("FACTS")
ax[2].semilogy(dfFACTS.index/10,dfFACTS.WLS,label="WLS",ls=":")
ax[2].semilogy(dfFACTS.index/10,dfFACTS.MAP_PMU,label="MAP PMU",ls=":")
# ax[2].semilogy(dfFACTS.index/100,dfFACTS.MAP_SCADA,label="MAP SCADA")

ax[0].legend()
ax[1].legend()
ax[2].legend()
# %%
