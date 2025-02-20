#%%

import pandas as pd
import numpy as np

sys="IEEE14_rakp2009"

caso="cargas1"
ini="x1"
medidasFACTS="SemMedidas"

df_refTrad=pd.read_csv("state_ref"+sys+caso+".csv",index_col=None)
# %%
df_refFACTS=pd.read_csv("state_FACTS_ref"+sys+caso+".csv",index_col=None)

#%%

df_Trad=pd.read_csv("state_"+sys+ini+medidasFACTS+caso+".csv",index_col=None)

df_FACTS=pd.read_csv("state_FACTS_"+sys+ini+medidasFACTS+caso+".csv",index_col=None)


#%%
df_Trad.sort_values(by=["scenario","sample","de","tipo"],inplace=True)
df_refTrad.sort_values(by=["scenario","sample","de","tipo"],inplace=True)
#%%

#%%

df_Trad["error"]=0.0

#%%

df_Trad["error"]=np.abs(df_Trad["val"]-df_Trad["val_ref"])

df_Trad.to_csv("ErrorsV_"+caso+".csv",index=None)
#%%

df_FACTS.sort_values(by=["scenario","sample","de","tipo"],inplace=True)
df_refFACTS.sort_values(by=["scenario","sample","de","tipo"],inplace=True)


df_FACTS["error"]=0.0


#%%

df_FACTS["error"]=np.abs(df_FACTS["val"]-df_FACTS["val_ref"])

df_FACTS.to_csv("ErrorsFACTS_"+caso+".csv",index=None)
#%%



