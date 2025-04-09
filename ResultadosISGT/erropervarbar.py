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

masks={}




vars={"x_tcsc",
"B_svc",
"UPFC_Vsh",
"UPFC_tsh",
"UPFC_Vse",
"UPFC_tse"}

for var in vars:
    masks[var]=dfstate_FACTS["tipo"]==var


#%%
SEs=["WLS","MAP_PMU","MAP_SCADA"]
MAE={}




for SE in SEs:
    MAE[SE]={}
    for var in vars:
        MAE[SE][var]=0

#%%

for SE in SEs:
    for var in vars:    
        MAE[SE][var]=np.mean(dfstate_FACTS[masks[var]&(dfstate_FACTS["method"]==SE)].error)


#%%
df=pd.DataFrame.from_dict(MAE)
df["type"]=df.index
#%%
df["type"]=df["type"].map({"UPFC_Vse":r"$V_{se}^{UPFC}$",
"UPFC_tse":r"$\theta_{se}^{UPFC}$",
"UPFC_Vsh":r"$V_{sh}^{UPFC}$",
"UPFC_tsh":r"$\theta^{UPFC}_{sh}$",
"x_tcsc":r"$x_{tcsc}$",
"B_svc":r"$b_{svc}$"})

#%%
df1=pd.DataFrame()
df1["type"]=df["type"]
df1["MAE"]=df["WLS"]
df1["SE"]="WLS"

df2=pd.DataFrame()
df2["type"]=df["type"]
df2["MAE"]=df["MAP_SCADA"]
df2["SE"]="Stage 1"


df3=pd.DataFrame()
df3["type"]=df["type"]
df3["MAE"]=df["MAP_PMU"]
df3["SE"]="Stage 2"
df=pd.concat([df1,df2,df3])


df["index"]=df.index

df.sort_values(by=["index","SE"],inplace=True)
#%%
k=0.5

fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(14*k,k*5))

sns.barplot(data=df,x="type",hue="SE",y="MAE",ax=ax,zorder=5,palette=pal)
ax.ticklabel_format(axis="y",style="sci",scilimits=(-3,-3))
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles=handles[0:], labels=labels[0:])

plt.grid(zorder=0)
plt.tight_layout()
plt.show()


plt.savefig("bargraph.pdf")

# %%

