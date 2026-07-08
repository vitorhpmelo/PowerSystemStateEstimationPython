#%%

import pandas as pd
import numpy as np


df_refTrad=pd.read_csv("state_refIEEE14_rakp2009.csv")
# %%
df_refFACTS=pd.read_csv("state_FACTS_refIEEE14_rakp2009.csv")

#%%

df_Trad=pd.read_csv("state_IEEE14_rakp2009x1SemMedidas.csv")

df_FACTS=pd.read_csv("state_FACTS_IEEE14_rakp2009x1SemMedidas.csv")


#%%

df_Trad["erro"]=0.0
for idx, item in df_Trad.iterrows():
    type=item["type"]
    fr=item["fr"]
    sce=item["scenario"]
    method=item["method"]
    mask=(df_refTrad["type"]==type) & (df_refTrad["fr"]==fr)  & (df_refTrad["scenario"]==sce)    
    df_Trad.at[idx,"erro"]=np.abs(item["val"]-df_refTrad[mask]["val"].values[0])
#%%


df_FACTS["erro"]=0.0
for idx, item in df_FACTS.iterrows():
    type=item["type"]
    fr=item["fr"]
    sce=item["scenario"]
    mask=(df_refFACTS["type"]==type) & (df_refFACTS["fr"]==fr)  & (df_refFACTS["scenario"]==sce)  
    df_FACTS.at[idx,"erro"]=np.abs(item["val"]-df_refFACTS[mask]["val"].values[0])

#%%
methods=list(set(df_Trad["method"].values))

error_theta={}
error_V={}
error_FACTS={}


for met in methods:
    maskV=(df_Trad["method"]==met) & (df_Trad["type"]=="v")
    maskt=(df_Trad["method"]==met) & (df_Trad["type"]=="theta")
    maskFACTS=(df_FACTS["method"]==met) 
    error_V[met]=np.mean(df_Trad[maskV].erro.values)
    error_theta[met]=np.mean(df_Trad[maskt].erro.values)
    error_FACTS[met]=np.mean(df_FACTS[maskFACTS].erro.values)

#%%

error_r={"V":error_V,"theta":error_theta,"FACTS":error_FACTS}
# %%
dfErro=pd.DataFrame(error_r)
#%%

dfErro.to_csv("MAE_variaveis2.csv")
#%%