#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


sys="IEEE14_rakp2009"

# casos=["v2facts"+str(i+1) for i in range(3)]

# casos=["v2cargas5","v2degrau5","v2rampa5","v2facts5"]

casos=["loadvar_sudden"]


for caso in casos:

    ini="x1"
    medidasFACTS="SemMedidas"


    dfErrorV=pd.read_csv("state_"+sys+ini+medidasFACTS+caso+".csv",index_col=None)
    dfErrorFACTS=pd.read_csv("state_FACTS_"+sys+ini+medidasFACTS+caso+".csv",index_col=None)



    scenarios=list(set(dfErrorV["scenario"].to_list()))
    methods=list(set(dfErrorV["method"].to_list()))


    dv={}
    dtheta={}
    dFACTS={}

    for met in methods:
        dv[met]=[]
        dtheta[met]=[]
        dFACTS[met]=[]



    for sce in scenarios:
        for met in methods:
            maskV=(dfErrorV["tipo"]=="v")&(dfErrorV["scenario"]==sce) & (dfErrorV["method"]==met)
            dv[met].append(np.mean(dfErrorV[maskV]["error"].values))
            maskt=(dfErrorV["tipo"]=="theta")&(dfErrorV["scenario"]==sce) & (dfErrorV["method"]==met)
            dtheta[met].append(np.mean(dfErrorV[maskV]["error"].values))
            maskf=(dfErrorFACTS["scenario"]==sce) & (dfErrorFACTS["method"]==met)
            dFACTS[met].append(np.mean(dfErrorFACTS[maskf]["error"].values))
            


    dfV=pd.DataFrame(dv)
    dftheta=pd.DataFrame(dtheta)

    dfFACTS=pd.DataFrame(dFACTS)



    dfV.to_csv("errosV_compilados"+caso+".csv",index=None)
    dftheta.to_csv("errostheta_compilados"+caso+".csv",index=None)
    dfFACTS.to_csv("errosFACTS_compilados"+caso+".csv",index=None)


#%%