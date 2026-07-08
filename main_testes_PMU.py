#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%
from src.classes import *
from src.readfiles import *
from src.networkstruc import *
from src.SE import *
from src.meas_sampl import *
import pandas as pd
import numpy as np
from src.networkcalc import *
from src.BadData import *
import numpy.linalg as liang
import scipy.sparse.linalg as sliang 


#%% Lê arquivos e constroi a estrutura da rede

sys="IEEE14_rakp2009"


dfDBAR,dfDBRAN,dfDMED,dfDFACTS=read_files(sys)


[bars,nbars,pv,pq,ind_i]=create_bus(dfDBAR)
[ram,nbran]=create_bran(dfDBRAN,ind_i)
#%%
[ramTCSC,nbranTCSC]=create_TCSC(dfDFACTS,ind_i)

[busSVC,BUS_SVC]=create_SVC(dfDFACTS,ind_i)

[ramUPFC,nbranUPFC]=create_UPFC(dfDFACTS,ind_i)




graph=create_graph(bars,ram)

addTCSCingraph(graph,ramTCSC)

addSVCingraph(graph,busSVC)

addUPFCingraph(graph,ramUPFC)





prec={"SCADAPF":0.01,"SCADAPI":0.01,"SCADAV":0.01,"SMP":0.01,"SMP":0.01,"SMV":0.01,"PSEUDO":0.01,"VIRTUAL":0.01,"PMU_If":0.001,"PMU_Iinj":0.001,"PMUs_V":0.001}

#%%
# dfDMED=create_DMED(sys,prec,graph,ram,ramUPFC)

#%%

dfDMED.loc[(dfDMED["type"]==0)|(dfDMED["type"]==1)|(dfDMED["type"]==2)|(dfDMED["type"]==3),"prec"]=0.02
dfDMED.loc[(dfDMED["type"]==10)|(dfDMED["type"]==11)|(dfDMED["type"]==12)|(dfDMED["type"]==13)|(dfDMED["type"]==14)|(dfDMED["type"]==15),"prec"]=0.001
dfDMED.loc[(dfDMED["type"]==4)|(dfDMED["type"]==5)|(dfDMED["type"]==6)|(dfDMED["type"]==7)|(dfDMED["type"]==8)|(dfDMED["type"]==9),"prec"]=0.001


medidas_virtuais_P=list(set(dfDMED[(dfDMED["type"]==0)&(dfDMED["zmed"]==0)]["fr"].to_list()).intersection(dfDMED[(dfDMED["type"]==1)&(dfDMED["zmed"]==0)]["fr"].to_list())) 

#%%





#%%
conv_noBC,nits_noBC,dfITsGN=SE_WLS_FACTS_noBC(graph,dfDMED,ind_i,flatstart=2)



# %%



cov=calcCovRes_com_FACTS(graph,dfDMED,ind_i)

df_RES=renorm_com_FACTS(graph,dfDMED,ind_i,cov)

df_RES.to_csv("teste_residuos.csv",index=None)
# %%

df_RES["Res"]=np.abs(df_RES["Res"])
df_RES.sort_values(by="Res")

# %%
df_RES.sort_values(by="Rn")
# %%
