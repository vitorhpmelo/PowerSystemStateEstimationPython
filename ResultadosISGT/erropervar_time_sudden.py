#%%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
#%%
pal=["#EF5850","#6060F0","#45A369","#8A7B36","#F0CB26","#1DF06D"]
file="SE_data/"
s="sudden3"

dfstate=pd.read_csv(file+'state_IEEE14_rakp2009x1SemMedidasloadvar_'+s+'.csv',index_col=None)
dfstate_FACTS=pd.read_csv(file+'state_FACTS_IEEE14_rakp2009x1SemMedidasloadvar_'+s+'.csv',index_col=None)
#%%
maskv=dfstate["tipo"]=="v"
maskt=dfstate["tipo"]=="theta"
buses=set(dfstate[dfstate["tipo"]=="v"].de)
#%%
SEs=["WLS","MAP_PMU","MAP_SCADA"]
MAEv={}
MAEf={}
MAEto={}


scenarios=list(set(dfstate["scenario"].values) )

for SE in SEs:
    MAEv[SE]=[]
    MAEf[SE]=[]
    MAEto[SE]=[]


for SE in SEs:
    for sce in scenarios:
        x=np.mean(dfstate[(dfstate["scenario"]==sce)&(maskv|maskt)&(dfstate["method"]==SE)].error)
        y=np.mean(dfstate_FACTS[(dfstate_FACTS["scenario"]==sce)&(dfstate_FACTS["method"]==SE)].error)   
        MAEv[SE].append(x)
        MAEf[SE].append(y)

        MAEto[SE].append((x+y)/2)

    MAEv[SE]=np.array(MAEv[SE])
    MAEf[SE]=np.array(MAEf[SE])

#%%
k=0.5
fig,ax=plt.subplots(nrows=1,ncols=2,figsize=(14*k,k*6))
t=np.array(range(1,1+len(MAEv["MAP_PMU"])))/10
ax[0].plot(t,MAEv["MAP_PMU"],label="MAP Stg 2",color=pal[2],marker="x",ms=5,ls="--")
# ax[0].plot(range(1,1+len(MAEv["MAP_SCADA"])),MAEv["MAP_SCADA"],label="MAP Stage 1",marker="d",color=pal[0])
ax[0].plot(t,MAEv["WLS"],label="Hyb WLS",color=pal[1],marker="^",ms=5,ls="--")

arrowprops = dict(
    arrowstyle="->",
    facecolor="k",
    connectionstyle="angle,angleA=0,angleB=90,rad=5"
    )

y=0
ax[0].annotate("Event 1",(1.5,y), xycoords='data',xytext=(0.5,4e-3), arrowprops=arrowprops)


ax[0].annotate("Event 2",(3.5-0.02,y), xycoords='data',xytext=(0.5,6e-3), arrowprops=arrowprops)



ax[0].annotate("Event 3",(5,y), xycoords='data',xytext=(4.2,3.5e-3), arrowprops=arrowprops)

ax[0].annotate("Event 4",(7,y), xycoords='data',xytext=(4.2,5e-3), arrowprops=arrowprops)

# ax[0].set_xticks(range(1,1+len(MAEv["WLS"])))
ax[0].ticklabel_format(axis="y",style="sci",scilimits=(-3,-3))
ax[0].set_xlim([0,8])
ax[0].set_xlabel(r"time (s)")
ax[0].set_ylabel(r"$MAE$")
ax[0].legend()
ax[0].set_title(r"Bus Voltages")
ax[0].grid()

ax[1].plot(t,MAEf["MAP_PMU"],label="MAP Stg 2",color=pal[2],marker="x",ms=5,ls="--")
ax[1].plot(t,MAEf["WLS"],label="Hyb WLS",color=pal[1],marker="^",ms=5,ls="--")
# ax[1].set_xticks(range(1,1+len(MAEf["WLS"])))
ax[1].ticklabel_format(axis="y",style="sci",scilimits=(-3,-3))
ax[1].set_xlabel(r"time (s)")
ax[1].set_xlim([0,8])
ax[1].set_ylabel(r"$MAE$")

ax[1].annotate("Event 1",(1.5,y), xycoords='data',xytext=(0.5,15e-3), arrowprops=arrowprops)


ax[1].annotate("Event 2",(3.5-0.02,y), xycoords='data',xytext=(0.5,22e-3), arrowprops=arrowprops)



ax[1].annotate("Event 3",(5,y), xycoords='data',xytext=(4.2,15e-3), arrowprops=arrowprops)

ax[1].annotate("Event 4",(7,y), xycoords='data',xytext=(4.2,22e-3), arrowprops=arrowprops)




ax[1].legend()




ax[1].set_title(r"FACTS Variables")
ax[1].grid()

plt.tight_layout()


# %%
plt.savefig("load_var_t_separado"+s+".pdf")
#%%%
k=0.42
fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(14*k,k*6.5))





plot1,=ax.plot(t,MAEto["MAP_PMU"],label="MAP Stg. 2",color=pal[2],marker="x",ms=5,ls="--",zorder=1)
plot2,=ax.plot(t,MAEto["WLS"],label="Hyb. WLS",color=pal[1],marker="^",ms=5,ls="--",zorder=1)
ax.set_xticks(range(1,1+len(MAEv["WLS"])))
ax.ticklabel_format(axis="y",style="sci",scilimits=(-3,-3))

# plot3=ax.hlines(7.09e-4,xmin=min(range(1,1+len(MAEv["WLS"]))),xmax=max(range(1,1+len(MAEv["WLS"]))),label="Hyb. WLS",ls="--",color=pal[0],zorder=0 )
# plot4=ax.hlines(3.14e-4,xmin=min(range(1,1+len(MAEv["WLS"]))),xmax=max(range(1,1+len(MAEv["WLS"]))),label="MAP Stg. 2",ls="--",colors="k",zorder=0)
ax.set_xlim([0,8])


ax.annotate("Event 1",(1.5,y), xycoords='data',xytext=(0.5,10e-3), arrowprops=arrowprops)


ax.annotate("Event 2",(3.5-0.02,y), xycoords='data',xytext=(2.5,15e-3), arrowprops=arrowprops)



ax.annotate("Event 3",(5,y), xycoords='data',xytext=(4.2,15e-3), arrowprops=arrowprops)

ax.annotate("Event 4",(7,y), xycoords='data',xytext=(6,15e-3), arrowprops=arrowprops)



ax.set_ylabel(r"$MAE$")
ax.set_xlabel(r"Time (s)")
l1=ax.legend(handles=[plot1,plot2],ncols=1,title="Load variation",loc="upper left")
ax.add_artist(l1)
# l2=ax.legend(handles=[plot3,plot4],ncols=1,title="Stationary loads",loc="upper right")

ax.grid()

plt.tight_layout()
plt.savefig("load_var_t_junto"+s+".pdf")


# %%
