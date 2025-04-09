#%%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
#%%
pal=["#EF5850","#6060F0","#45A369","#8A7B36","#F0CB26","#1DF06D"]

dfstate=pd.read_csv('state_IEEE14_rakp2009x1SemMedidasesta.csv',index_col=None)
dfstate_FACTS=pd.read_csv('state_FACTS_IEEE14_rakp2009x1SemMedidasesta.csv',index_col=None)
#%%
maskv=dfstate["tipo"]=="v"
maskt=dfstate["tipo"]=="teta"
buses=set(dfstate[dfstate["tipo"]=="v"].de)
#%%
SEs=["WLS","MAP_PMU","MAP_SCADA"]
MAEv={}
STDv={}
MAXv={}

MAEt={}
STDt={}
MAXt={}



for SE in SEs:
    MAEv[SE]=[]
    STDv[SE]=[]
    MAXv[SE]=[]
    MAEt[SE]=[]
    STDt[SE]=[]
    MAXt[SE]=[]
#%%

for SE in SEs:
    for bus in range(len(buses)):    
        MAEv[SE].append(np.mean(dfstate[maskv&(dfstate["de"]==bus)&(dfstate["method"]==SE)].error))
        STDv[SE].append(np.std(dfstate[maskv&(dfstate["de"]==bus)&(dfstate["method"]==SE)].error))
        MAXv[SE].append(np.max(dfstate[maskv&(dfstate["de"]==bus)&(dfstate["method"]==SE)].error))

        MAEt[SE].append(np.mean(dfstate[maskt&(dfstate["de"]==bus)&(dfstate["method"]==SE)].error))
        STDt[SE].append(np.std(dfstate[maskt&(dfstate["de"]==bus)&(dfstate["method"]==SE)].error))
        MAXt[SE].append(np.max(dfstate[maskt&(dfstate["de"]==bus)&(dfstate["method"]==SE)].error))
    MAEv[SE]=np.array(MAEv[SE])
    STDv[SE]=np.array(STDv[SE])
    MAXv[SE]=np.array(MAXv[SE])
    MAEt[SE]=np.array(MAEt[SE])
    STDt[SE]=np.array(STDt[SE])
    MAXt[SE]=np.array(MAXt[SE])
#%%
k=0.5
fig,ax=plt.subplots(nrows=2,ncols=1,figsize=(14*k,k*7))

ax[0].plot(range(1,1+len(MAEv["MAP_PMU"])),MAEv["MAP_PMU"],label="MAP Stage 2",marker="d",color=pal[0])
ax[0].plot(range(1,1+len(MAEv["MAP_SCADA"])),MAEv["MAP_SCADA"],label="MAP Stage 1",marker="x",color=pal[1])
ax[0].plot(range(1,1+len(MAEv["WLS"])),MAEv["WLS"],label="MAP Stage 1",marker="x",color=pal[2])
ax[0].set_xticks(range(1,1+len(MAEv["WLS"])))
ax[0].ticklabel_format(axis="y",style="sci",scilimits=(-3,-3))
ax[0].set_xlim([1,16])
ax[0].set_ylabel(r"$MAE$")
ax[0].set_title(r"$V$")
ax[0].grid()

ax[1].plot(range(1,1+len(MAEt["MAP_PMU"])),MAEt["MAP_PMU"],label="MAP Stage 2",marker="d",color=pal[0])
ax[1].plot(range(1,1+len(MAEt["MAP_SCADA"])),MAEt["MAP_SCADA"],label="MAP Stage 1",marker="x",color=pal[1])
ax[1].plot(range(1,1+len(MAEt["WLS"])),MAEt["WLS"],label="MAP Stage 1",marker="x",color=pal[2])
ax[1].set_xticks(range(1,1+len(MAEt["WLS"])))
ax[1].ticklabel_format(axis="y",style="sci",scilimits=(-3,-3))
ax[1].set_xlim([1,16])
ax[1].set_ylabel(r"$MAE$")

ax[1].set_title(r"$\theta$")
ax[1].grid()

plt.tight_layout()
plt.close()

# %%


k=0.45
fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(14*k,k*5.5))




ax.plot(range(1,1+len(MAEv["MAP_PMU"])),(MAEv["MAP_PMU"]+MAEt["MAP_PMU"])/2,label="MAP Stage 2",marker="d",color=pal[0])
ax.plot(range(1,1+len(MAEv["MAP_SCADA"])),(MAEv["MAP_SCADA"]+MAEt["MAP_SCADA"])/2,label="MAP Stage 1",marker="x",color=pal[1])
ax.plot(range(1,1+len(MAEv["WLS"])),(MAEv["WLS"]+MAEt["WLS"])/2,label="Hybrid WLS",marker="x",color=pal[2])
ax.set_xticks(range(1,1+len(MAEv["WLS"])))
ax.ticklabel_format(axis="y",style="sci",scilimits=(-3,-3))
ax.set_xlim([1,16])
ax.set_ylabel(r"$MAE$")
ax.set_xlabel(r"Bus")
ax.set_ylim(ymax=2.8e-3)
ax.legend(ncols=3)




ax.grid()

plt.tight_layout()
plt.savefig("error_per_bus.pdf")


# %%
