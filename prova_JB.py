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
conv=load_flow_FACTS(graph,inici=1,prt=1,itmax=20)
#%%



ram.update(ramTCSC)

save_DMED_fp(graph,ram,sys,ramUPFC)


#%%

prec={}

dfDMED=create_DMED(sys,prec,graph,ram,ramUPFC)


dfDMED["prec"]= 0.02*3/np.abs(dfDMED["zmed"])

dfDMED.replace([np.inf,-np.inf],0.02,inplace=True)



# %%

sigma=np.abs(dfDMED["zmed"])*dfDMED["prec"]/3

#%%


dfDMED["sigma"]=sigma

#%%

dfDMED.to_csv(sys+"/DMED_sem_eg.csv")

#%%


EGs=[[0,4,-1],[1,4,-1]]


for eg in EGs: 
    maskP=(dfDMED["type"]==eg[0])&(dfDMED["de"]==eg[1])&(dfDMED["para"]==eg[2])

    idx=dfDMED[maskP].index[0]

    dfDMED.at[idx,"zmed"]=dfDMED.at[idx,"zmed"]-20*dfDMED.at[idx,"sigma"] 


dfDMED.to_csv(sys+"/DMED_D.csv",index=None,float_format="%.7f")


#%%


conv_noBC,nits_noBC,dfITsGN=SS_WLS_FACTS_noBC(graph,dfDMED,ind_i,tol=1e-4,tol2=1e-4,flatstart=2)
# %%



cov=calcCovRes_com_FACTS(graph,dfDMED,ind_i)

df_RES=renorm_com_FACTS(graph,dfDMED,ind_i,cov)

# %%

df_RES["Res"]=np.abs(df_RES["Res"])

df_RES.sort_values(by="Rn")


# %%


tipo=0
de=4
para=-1

mask=(dfDMED["type"]==tipo)&(dfDMED["de"]==de)&(dfDMED["para"]==para)
#%%

idx=dfDMED[mask].index[0]
#%%
dfDMED.drop(index=idx,inplace=True)
#%%



conv_noBC,nits_noBC,dfITsGN=SS_WLS_FACTS_noBC(graph,dfDMED,ind_i,tol=1e-4,tol2=1e-4,flatstart=2)
# %%



cov=calcCovRes_com_FACTS(graph,dfDMED,ind_i)

df_RES=renorm_com_FACTS(graph,dfDMED,ind_i,cov)

# %%

df_RES["Res"]=np.abs(df_RES["Res"])

df_RES.sort_values(by="Rn")

#%%