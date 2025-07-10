#%%
import pandas as pd
import matplotlib.pyplot as plt

caso="loadvar"

dfV=pd.read_csv("errosV_compilados"+caso+".csv")

dftheta=pd.read_csv("errostheta_compilados"+caso+".csv")
dfFACTS=pd.read_csv("errosFACTS_compilados"+caso+".csv")
#%%


fig, ax = plt.subplots(nrows=1,ncols=3,figsize=(16,5))

ax[0].set_xlabel("tempo (s)")
ax[0].set_ylabel("MAE")

ax[0].set_title("V")

ax[0].semilogy(dfV.index/10,dfV.WLS.values,label="WLS",ls=":")
ax[0].semilogy(dfV.index/10,dfV.MAP_PMU.values,label="MAP PMU",ls=":")
# ax[0].semilogy(dfV.index/10,dfV.MAP_SCADA.values,label="MAP SCADA")

ax[1].set_xlabel("tempo (s)")
ax[1].set_ylabel("MAE")

ax[1].set_title(r"$\theta$")
ax[1].semilogy(dftheta.index/10,dftheta.WLS,label="WLS",ls=":")
ax[1].semilogy(dftheta.index/10,dftheta.MAP_PMU,label="MAP PMU",ls=":")
# ax[1].semilogy(dftheta.index/100,dftheta.MAP_SCADA,label="MAP SCADA")

ax[2].set_xlabel("tempo (s)")
ax[2].set_ylabel("MAE")
ax[2].set_title("FACTS")
ax[2].semilogy(dfFACTS.index/10,dfFACTS.WLS,label="WLS",ls=":")
ax[2].semilogy(dfFACTS.index/10,dfFACTS.MAP_PMU,label="MAP PMU",ls=":")
# ax[2].semilogy(dfFACTS.index/100,dfFACTS.MAP_SCADA,label="MAP SCADA")

ax[0].legend()
ax[1].legend()
ax[2].legend()

ax[0].grid()
ax[1].grid()
ax[2].grid()
# %%
