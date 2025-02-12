#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



dfErrorV=pd.read_csv("ErrorsV_loadvar3.csv")
dfErrorFACTS=pd.read_csv("ErrorsFACTS_loadvar3.csv")
#%%


scenarios=list(set(dfErrorV["scenario"].to_list()))
methods=list(set(dfErrorV["method"].to_list()))

#%%
dv={}
dteta={}
dFACTS={}

for met in methods:
    dv[met]=[]
    dteta[met]=[]
    dFACTS[met]=[]



for sce in scenarios:
    for met in methods:
        maskV=(dfErrorV["tipo"]=="v")&(dfErrorV["scenario"]==sce) & (dfErrorV["method"]==met)
        dv[met].append(np.mean(dfErrorV[maskV]["error"].values))
        maskt=(dfErrorV["tipo"]=="teta")&(dfErrorV["scenario"]==sce) & (dfErrorV["method"]==met)
        dteta[met].append(np.mean(dfErrorV[maskV]["error"].values))
        maskf=(dfErrorFACTS["scenario"]==sce) & (dfErrorFACTS["method"]==met)
        dFACTS[met].append(np.mean(dfErrorFACTS[maskf]["error"].values))
        
# %%

dfV=pd.DataFrame(dv)
dfteta=pd.DataFrame(dteta)
#%%
dfFACTS=pd.DataFrame(dFACTS)


# %%
dfV.to_csv("errosV_compilados4.csv",index=None)
dfteta.to_csv("errosteta_compilados4.csv",index=None)
dfFACTS.to_csv("errosFACTS_compilados4.csv",index=None)


#%%