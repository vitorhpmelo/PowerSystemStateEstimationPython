#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


sys="IEEE14_rakp2009"

# casos=["v2facts"+str(i+1) for i in range(3)]

# casos=["v2cargas5","v2degrau5","v2rampa5","v2facts5"]

casos=["v3facts5"]


for caso in casos:

    ini="x1"
    medidasFACTS="SemMedidas"


    dfErrorV=pd.read_csv("state_"+sys+ini+medidasFACTS+caso+".csv",index_col=None)
    dfErrorFACTS=pd.read_csv("state_FACTS_"+sys+ini+medidasFACTS+caso+".csv",index_col=None)



    scenarios=list(set(dfErrorV["scenario"].to_list()))
    methods=list(set(dfErrorV["method"].to_list()))


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
            


    dfV=pd.DataFrame(dv)
    dfteta=pd.DataFrame(dteta)

    dfFACTS=pd.DataFrame(dFACTS)



    dfV.to_csv("errosV_compilados"+caso+".csv",index=None)
    dfteta.to_csv("errosteta_compilados"+caso+".csv",index=None)
    dfFACTS.to_csv("errosFACTS_compilados"+caso+".csv",index=None)


#%%