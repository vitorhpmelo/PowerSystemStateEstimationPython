#%%

import pandas as pd
import numpy as np


df_refTrad=pd.read_csv("state_refIEEE14_rakp2009loadvar4.csv",index_col=None)
# %%
df_refFACTS=pd.read_csv("state_FACTS_refIEEE14_rakp2009loadvar4.csv",index_col=None)

#%%

df_Trad=pd.read_csv("state_IEEE14_rakp2009x1SemMedidasloadvar4.csv",index_col=None)

df_FACTS=pd.read_csv("state_FACTS_IEEE14_rakp2009x1SemMedidasloadvar4.csv",index_col=None)


#%%
df_Trad.sort_values(by=["scenario","sample","de","tipo"],inplace=True)
df_refTrad.sort_values(by=["scenario","sample","de","tipo"],inplace=True)
#%%

#%%

df_Trad["error"]=0.0
df_Trad["val_lf"]=0.0

methods=list(set(df_Trad["method"].tolist()))
samples=list(set(df_Trad["sample"].tolist()))
scenarios=list(set(df_Trad["scenario"].tolist()))
#%%

for met in methods:
    for sam in samples:
        for sce in scenarios:
            mask1=(df_Trad["scenario"]==sce) & (df_Trad["sample"]==sam)  & (df_Trad["method"]==met)
            mask2=(df_refTrad["scenario"]==sce)
            df_Trad.loc[mask1,"val_lf"]=df_refTrad.loc[mask2,"val"].values

#%%

df_Trad["error"]=np.abs(df_Trad["val"]-df_Trad["val_lf"])

df_Trad.to_csv("ErrorsV_loadvar4.csv",index=None)
#%%

df_FACTS.sort_values(by=["scenario","sample","de","tipo"],inplace=True)
df_refFACTS.sort_values(by=["scenario","sample","de","tipo"],inplace=True)


df_FACTS["error"]=0.0
df_FACTS["val_lf"]=0.0

#%%
for met in methods:
    for sam in samples:
        for sce in scenarios:
            mask1=(df_FACTS["scenario"]==sce) & (df_FACTS["sample"]==sam)  & (df_FACTS["method"]==met)
            mask2=(df_refFACTS["scenario"]==sce)
            df_FACTS.loc[mask1,"val_lf"]=df_refFACTS.loc[mask2,"val"].values
#%%

df_FACTS["error"]=np.abs(df_FACTS["val"]-df_FACTS["val_lf"])

df_FACTS.to_csv("ErrorsFACTS_loadvar4.csv",index=None)
#%%