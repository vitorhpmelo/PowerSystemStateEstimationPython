#%%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.family'] = 'Liberation Sans'

# Also keep your existing settings
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

#%%
pal=["#EF5850","#6060F0","#45A369","#8A7B36","#F0CB26","#1DF06D"]
file="SE_data/"
s="sudden2"

dfstate=pd.read_csv(file+'state_IEEE14_rakp2009x1SemMedidasloadvar_'+s+'.csv',index_col=None)
dfstate_FACTS=pd.read_csv(file+'state_FACTS_IEEE14_rakp2009x1SemMedidasloadvar_'+s+'.csv',index_col=None)

dfdata1=pd.concat([dfstate,dfstate_FACTS])

s="sudden3"
dfstate_3=pd.read_csv(file+'state_IEEE14_rakp2009x1SemMedidasloadvar_'+s+'.csv',index_col=None)
dfstate_FACTS_3=pd.read_csv(file+'state_FACTS_IEEE14_rakp2009x1SemMedidasloadvar_'+s+'.csv',index_col=None)

dfdata2=pd.concat([dfstate_3,dfstate_FACTS_3])

#%%

#%%
SEs=["WLS","MAP_PMU","MAP_SCADA"]
MAEv={}
MAEf={}
MAEto={}
MAEto2={}

scenarios=list(set(dfdata1["scenario"].values) )

for SE in SEs:
    MAEto[SE]=[]
    MAEto2[SE]=[]

#%%
for SE in SEs:
    for sce in scenarios:
        x=np.mean(dfdata1[(dfdata1["scenario"]==sce)&(dfdata1["method"]==SE)].error)
        y=np.mean(dfdata2[(dfdata2["scenario"]==sce)&(dfdata2["method"]==SE)].error)   

        MAEto[SE].append(x)
        MAEto2[SE].append(y)




#%%
k=0.39
fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(14*k,k*5))
t=np.array(range(1,1+len(MAEto["MAP_PMU"])))/10
ax.plot(t,MAEto["MAP_PMU"],label="Original Meas Set",color=pal[2],marker="x",ms=5,ls="--")
# ax[0].plot(range(1,1+len(MAEv["MAP_SCADA"])),MAEv["MAP_SCADA"],label="MAP Stage 1",marker="d",color=pal[0])
ax.plot(t,MAEto2["MAP_PMU"],label="Modified Meas Set",color="#092e1f",marker="d",ms=5,ls="--")

arrowprops = dict(
    arrowstyle="->",
    facecolor="k",
    connectionstyle="angle,angleA=0,angleB=90,rad=5"
    )

y=0


ax.annotate("Event 3",(5,y+0.1e-3), xycoords='data',xytext=(4.3,1.5e-3), arrowprops=arrowprops)

ax.annotate("Event 4",(7,y+0.1e-3), xycoords='data',xytext=(6,3e-3), arrowprops=arrowprops)

# ax[0].set_xticks(range(1,1+len(MAEv["WLS"])))
ax.ticklabel_format(axis="y",style="sci",scilimits=(-3,-3))
ax.set_xlim([4.2,8])
ax.set_ylim([0,4e-3])
ax.set_xlabel(r"Time (s)")
ax.set_ylabel(r"$MAE$")
ax.legend()
# ax.set_title(r"Bus Voltages")
ax.grid()

plt.tight_layout()


# %%
plt.savefig("load_var_t_separado_comp.pdf")
#%%%
