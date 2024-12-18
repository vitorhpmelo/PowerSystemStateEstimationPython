#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%
from classes import *
from readfiles import *
from networkstruc import *
from SS import *
from meas_sampl import *
import pandas as pd
import numpy as np
from networkcalc import *
from BadData import *
import numpy.linalg as liang
import scipy.sparse.linalg as sliang 


#%% Lê arquivos e constroi a estrutura da rede

sys="IEEE14_provaJB"


dfDBAR,dfDBRAN,dfDMED,dfDFACTS=read_files(sys)



[bars,nbars,pv,pq,ind_i]=creat_bar(dfDBAR)
[ram,nbran]=create_bran(dfDBRAN,ind_i)
#%%
[ramTCSC,nbranTCSC]=create_TCSC(dfDFACTS,ind_i)

[busSVC,BUS_SVC]=create_SVC(dfDFACTS,ind_i)

[ramUPFC,nbranUPFC]=create_UPFC(dfDFACTS,ind_i)




graph=create_graph(bars,ram)

addTCSCingraph(graph,ramTCSC)

addSVCingraph(graph,busSVC)

addUPFCingraph(graph,ramUPFC)




#%%

conv_noBC,nits_noBC,dfITsGN=SS_WLS_FACTS_noBC(graph,dfDMED,ind_i,tol=1e-4,tol2=1e-4,flatstart=2)
# %%



cov=calcCovRes_com_FACTS(graph,dfDMED,ind_i)

df_RES=renorm_com_FACTS(graph,dfDMED,ind_i,cov)

# %%

df_RES["Res"]=np.abs(df_RES["Res"])

df_RES.sort_values(by="Rn",ascending=True,inplace=True)
#%%

df_RES["Tipo"]=df_RES["Tipo"].map({0:"Pinj",1:"Qinj",2:"Pf",3:"Qf",4:"V"})

print(df_RES.iloc[-1])

# %%
