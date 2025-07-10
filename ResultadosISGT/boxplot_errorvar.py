#%%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
#%%
pal=["#EF5850","#6060F0","#45A369","#8A7B36","#F0CB26","#1DF06D"]
file="SE_data/"
s=""

dfstate=pd.read_csv(file+'state_IEEE14_rakp2009x1SemMedidasloadvar'+s+'.csv',index_col=None)
dfstate_FACTS=pd.read_csv(file+'state_FACTS_IEEE14_rakp2009x1SemMedidasloadvar'+s+'.csv',index_col=None)
#%%
dfdata=pd.concat([dfstate,dfstate_FACTS])
#%%

dfdata



buses=set(dfstate[dfstate["tipo"]=="v"].de)
#%%



#%%
k=0.4
fig,ax =plt.subplots(ncols=2,nrows=1,figsize=(10*k,k*4))

# %%


dfstate=dfstate[dfstate["method"]!="MAP_SCADA"]

# %%
dfstate_FACTS=dfstate_FACTS[dfstate_FACTS["method"]!="MAP_SCADA"]


dfstate_FACTS["tipo"]="FACTS"


dfdata=pd.concat([dfstate,dfstate_FACTS])

dfdata["tipo"]=dfdata["tipo"].map({"FACTS":"FACTS","v":r"$v$","theta":r"$\theta$"})

dfdata["method"]=dfdata["method"].map({"WLS":"WLS Hyb.","MAP_PMU":"MAP Stg. 2"})

dfdata.rename(columns={"method":"Method","error":"Error"},inplace=True)

k=0.5
fig,ax =plt.subplots(ncols=1,nrows=1,figsize=(10*k,k*6))

sns.boxplot(dfdata,y="Error",x="tipo",hue="Method",showfliers=False,palette=pal,ax=ax)

plt.xlabel("Variable Type")

plt.ticklabel_format(axis="y",style="sci",scilimits=(-3,-3))
plt.grid()
plt.tight_layout()
plt.savefig("boxplot_loadvar.pdf")


# %%
