#%% Simulações from monte carlo
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from src.SE_Bayesian import *
import matplotlib.pyplot as plt


#%% Lê arquivos e constroi a estrutura da rede

sys="IEEE14"
measFACTS=False

if measFACTS==True: #nomeclatura dos arquivos from entrada
    Meas="ComMedidas"
else:
    Meas="SemMedidas"



dfDBAR,dfDBRAN,dfDMED,dfDFACTS=read_files(sys) # lê arquivos


[bars,nbars,pv,pq,ind_i]=create_bus(dfDBAR)
[ram,nbran]=create_bran(dfDBRAN,ind_i)

[ramTCSC,nbranTCSC]=create_TCSC(dfDFACTS,ind_i)

[busSVC,BUS_SVC]=create_SVC(dfDFACTS,ind_i)

[ramUPFC,nbranUPFC]=create_UPFC(dfDFACTS,ind_i)

graph=create_graph(bars,ram)


#casos from compensação

dfcasos=pd.DataFrame(data={"TCSC":[10],"SVC":[1],"UPFC_flow":[-10],"UPFC_V":[1],"TCSC_ini":[-0.05],"SVC_ini":[0.10]})
#%%
dDMEDfps={}
dState_ref={}
dStateTCSC_ref={}
for idx, row in dfcasos.iterrows():

    try:    
        conv=power_flow_FACTS(graph,inici=1,prt=1,itmax=20,printgrad=0,printres=0)
    except:
        conv=0

    #get states and 
    dDMEDfps[idx]=save_DMEAS_ac_pf(graph,ram,sys,ramUPFC)
    dState_ref[idx]=get_state(graph)
    

#%%
dfSATES_ref=pd.DataFrame() #salva os valores from referência das variáveis from estado normais


for key,item in dState_ref.items():
    df=item
    df["method"]="PF"
    df["scenario"]=key
    dfSATES_ref=pd.concat([dfSATES_ref,df])
    
#%%
dfSATES_ref.to_csv("ResultadosISGT/state_ref"+sys+".csv")

#%%




dfDMEDs={}
for idx, row in dfcasos.iterrows():
    prec={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.02,"SMP":0.05,"SMV":0.03,"PSEUDO":0.3,"VIRTUAL":1e-5,"TCSCvar":0.01,"SVCvar":0.01,"UPFCt_sh":0.01,"UPFCV_sh":0.01,"UPFCt_se":0.01,"UPFCV_se":0.01}
    dfDMED=create_DMEAS_old(sys,prec,graph,ram,ramUPFC,dfDMEASpf=dDMEDfps[idx])
    dfDMEDs[idx]=dfDMED.copy()


prec_LIM=0.005


#%%

N=100

dState_MAP_SCADA={}
dState_MAP_PMU={}
dState_WLS={}
dfITS=pd.DataFrame()
dconv={}
dconv["n"]=[]
dconv["convMAP_SCADA"]=[]
dconv["convMAP_PMU"]=[]
dconv["convWLS"]=[]
dconv["nitsMAP_SCADA"]=[]
dconv["nitsMAP_PMU"]=[]
dconv["nitsWLS"]=[]
dconv["case"]=[]

np.random.seed(1)
for idx, row in dfcasos.iterrows():

    dState_MAP_SCADA[idx]=[]
    dState_MAP_PMU[idx]=[]
    dState_WLS[idx]=[]


    for n in range(N): 
        dfDMED=insert_res(dfDMEDs[idx])


        dfDMEDSCADA=dfDMED[(dfDMED["prec"]>prec_LIM)].copy()

        dfDMEDPMU=dfDMED[(dfDMED["prec"]<prec_LIM)].copy()

     
        conv_WLS,nits_WLS,dfITsWLS=SE_WLS_FACTS_noBC(graph,dfDMED,ind_i,printgrad=0,printres=0,printits=1,flatstart=2,tol=1e-6,tol2=7,prec_virtual=1e-5)


        
        if conv_WLS==True:
            dState_WLS[idx].append(get_state(graph,n))
        
        conv_MAP_SCADA,nits_MAP_SCADA,dfITsMAP_SCADA=SE_WLS_FACTS_noBC(graph,dfDMEDSCADA,ind_i,flatstart=2,printits=1,tol2=1e-6,tol=1e-7,prec_virtual=1e-5)
        
        if conv_MAP_SCADA==True:
            dState_MAP_SCADA[idx].append(get_state(graph,n))

        if conv_MAP_SCADA==True:
            priori=calc_priori(graph,dfDMEDSCADA,dfDMEDPMU,ind_i,lamb=1e-5,prec_virtual=1e-5)
            conv_MAP_PMU,nits_MAP_PMU,dfITsMAP_PMU=SE_MAP_FACTS_withBC(graph,priori,dfDMEDPMU,ind_i,tol2=7,tol=1e-6,flatstart=1,prec_virtual=1e-5,printits=1)
        else:
            conv_MAP_PMU=0
            nits_MAP_PMU=30
            dfITsMAP_PMU=pd.DataFrame()
            
        if conv_MAP_PMU==True:
            dState_MAP_PMU[idx].append(get_state(graph,n))


        dconv["convWLS"].append(conv_WLS)
        dconv["convMAP_SCADA"].append(conv_MAP_SCADA)
        dconv["convMAP_PMU"].append(conv_MAP_PMU)
        dconv["nitsWLS"].append(nits_WLS)
        dconv["nitsMAP_SCADA"].append(nits_MAP_SCADA)
        dconv["nitsMAP_PMU"].append(nits_MAP_PMU)

        dconv["n"].append(n)
        dconv["convMAP_SCADA"].append(conv_MAP_SCADA)
        dconv["convMAP_PMU"].append(conv_MAP_PMU)
        dconv["convWLS"].append(conv_WLS)
        dconv["nitsMAP_SCADA"].append(nits_MAP_SCADA)
        dconv["nitsMAP_PMU"].append(nits_MAP_PMU)
        dconv["nitsWLS"].append(nits_WLS)
        dconv["case"].append(idx)

        if not dfITsMAP_SCADA.empty:
            dfITsMAP_SCADA["method"]="MAP_SCADA"
            dfITsMAP_SCADA["case"]=idx
            dfITsMAP_SCADA["n"]=n
        if not dfITsMAP_PMU.empty:
            dfITsMAP_PMU["method"]="MAP_PMUs"
            dfITsMAP_PMU["case"]=idx
            dfITsMAP_PMU["n"]=n
        if not dfITsWLS.empty:
            dfITsWLS["method"]="WLS"
            dfITsWLS["case"]=idx
            dfITsWLS["n"]=n
        dfITS=pd.concat([dfITS,dfITsMAP_SCADA,dfITsMAP_PMU,dfITsWLS])

#%%

dfSATES=pd.DataFrame()


#%%


for key,item in dState_WLS.items():
    if len(item)>0:
        df=pd.concat(item)
        df["method"]="WLS"
        df["scenario"]=key
        dfSATES=pd.concat([dfSATES,df])
        


for key,item in dState_MAP_SCADA.items():
    if len(item)>0:
        df=pd.concat(item)
        df["method"]="MAP_SCADA"
        df["scenario"]=key
        
        dfSATES=pd.concat([dfSATES,df])



for key,item in dState_MAP_PMU.items():
    if len(item)>0:
        df=pd.concat(item)
        df["method"]="MAP_PMU"
        df["scenario"]=key
        dfSATES=pd.concat([dfSATES,df])





#%%

#%%
dfSATES.to_csv("ResultadosISGT/state_"+sys+Meas+".csv")
#%%

for idx,row in dfSATES_ref.iterrows():
    mask = (dfSATES["type"]==row["type"])&(dfSATES["bus"]==row["bus"])
    dfSATES.loc[mask,"val_ref"]=row["val"]
# %%


methods=list(set(dfSATES["method"].tolist()))
vars=list(set(dfSATES["type"].tolist()))
# %%
dfSATES["error"]=(dfSATES["val"]-dfSATES["val_ref"]).abs()
#%%
methods=["MAP_PMU","WLS"]
d_errors={}
for method in methods:
    
    d_errors[method]={}
    for var in vars:
        mask=(dfSATES["method"]==method)&(dfSATES["type"]==var)
        d_errors[method][var]= dfSATES.loc[mask,"error"].mean()
# %%


fig, ax = plt.subplots(len(vars), 1, figsize=(10, 3*len(vars)))

for i, var in enumerate(vars):
    errors = [d_errors[method][var] for method in methods]
    ax[i].bar(range(len(methods)), errors, alpha=0.8)
    ax[i].set_ylabel("Mean Error")
    ax[i].set_title(f"Variable: {var}")
    ax[i].set_xticks(range(len(methods)))
    ax[i].set_xticklabels(methods, rotation=45)
    ax[i].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()
# %%
dfErrors = pd.DataFrame(d_errors).T
dfErrors.to_csv("ResultadosISGT/errors_"+sys+Meas+".csv")
print(dfErrors)
# %%
