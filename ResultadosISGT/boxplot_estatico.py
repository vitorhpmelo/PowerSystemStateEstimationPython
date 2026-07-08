#%%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
#%%
dfstate=pd.read_csv('state_IEEE14_rakp2009x1SemMedidasesta.csv',index_col=None)
dfstate_FACTS=pd.read_csv('state_FACTS_IEEE14_rakp2009x1SemMedidasesta.csv',index_col=None)


# %%
dfdata=dfstate_FACTS.copy()
#%%
dfdata["type"]="FACTS"


#%%

dfdata=pd.concat([dfstate,dfdata])
dfdata.rename(columns={"type":"Var"},inplace=True)
#%%

dfdata["method"]=dfdata["method"].map({"WLS":"WLS Hybrid","MAP_SCADA":"MAP Stage 1","MAP_PMU":"MAP Stage 2"})
palette=["#EF5850","#6060F0","#45A369","#8A7B36","#F0CB26","#1DF06D"]
pal=sns.color_palette(palette,len(palette))
#%%
dfdata.sort_values(by=["method"],inplace=True)
k=0.5
fig,ax =plt.subplots(ncols=1,nrows=1,figsize=(10*k,k*6))

dfdata["Var"]=dfdata["Var"].map({"v":"V","":r"$\theta$","FACTS":"FACTS"})

sns.boxplot(dfdata,y="error",x="method",hue="Var",showfliers=False,palette=pal,ax=ax)

plt.xlabel("Method")

plt.ticklabel_format(axis="y",style="sci",scilimits=(-3,-3))


plt.grid()
plt.tight_layout()
# %%
plt.savefig("boxplot_errors.pdf")
# %%
