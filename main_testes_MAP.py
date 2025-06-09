#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de excução simples do Estimador Bayesiano para fusão de informação em comparação com o EE WLS tradicional
"""


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
from SS_Bayesian import *
import matplotlib.pyplot as plt 



#%% Lê arquivos e constroi a estrutura da rede

sys="IEEE14_rakp2009"


dfDBAR,dfDBRAN,dfDMED,dfDFACTS=read_files(sys)


[bars,nbars,pv,pq,ind_i]=creat_bus(dfDBAR)
[ram,nbran]=create_bran(dfDBRAN,ind_i)
#%%
[ramTCSC,nbranTCSC]=create_TCSC(dfDFACTS,ind_i)

[busSVC,BUS_SVC]=create_SVC(dfDFACTS,ind_i)

[ramUPFC,nbranUPFC]=create_UPFC(dfDFACTS,ind_i)




graph=create_graph(bars,ram)

addTCSCingraph(graph,ramTCSC)

addSVCingraph(graph,busSVC)

addUPFCingraph(graph,ramUPFC)





dfTCSC_original_values={}
dfsvc_original_values={}
dfUPFC_original_values={}
for key ,tcsc in ramTCSC.items():
    dfTCSC_original_values[key]=tcsc.Pfesp
for key,svc in busSVC.items():
    dfsvc_original_values[key]=graph[key].bar.V
for key,upfc in ramUPFC.items():
    dfUPFC_original_values[key]={}
    dfUPFC_original_values[key]["Psp"]=upfc.Psp_set
    dfUPFC_original_values[key]["Qsp"]=upfc.Qsp_set
    dfUPFC_original_values[key]["Vp"]=graph[upfc.p].bar.V
        


dfcasos=pd.DataFrame(data={"TCSC":[15],"SVC":[1],"UPFC_flow":[-10],"UPFC_V":[1],"TCSC_ini":[-0.01],"SVC_ini":[-1.0]})
#%%
dDMEDfps={}
dState_ref={}
dStateTCSC_ref={}
for idx, row in dfcasos.iterrows():
    for key ,tcsc in ramTCSC.items():
        tcsc.Pfesp=dfTCSC_original_values[key]*(1+(row["TCSC"]/100))
        tcsc.xtcsc_ini=row["TCSC_ini"]
    for key,svc in busSVC.items():
        graph[key].bar.V=dfsvc_original_values[key]*(1+(row["SVC"]/100))
        svc.Bini=row["SVC_ini"]
    for key,upfc in ramUPFC.items():
        upfc.Psp_set=dfUPFC_original_values[key]["Psp"]*(1+(row["UPFC_flow"]/100))
        upfc.Qsp_set=dfUPFC_original_values[key]["Psp"]*(1+(row["UPFC_flow"]/100))
        graph[upfc.p].bar.V=dfUPFC_original_values[key]["Vp"]*(1+(row["UPFC_V"]/100))

    try:    
        conv=load_flow_FACTS(graph,inici=1,prt=1,itmax=20,printgrad=0,printres=0)
    except:
        conv=0

    #get states and 
    if conv==1:
        ram.update(ramTCSC)
        dDMEDfps[idx]=save_DMED_fp(graph,ram,sys,ramUPFC)
        dState_ref[idx]=get_state(graph)
        dStateTCSC_ref[idx]=get_state_FACTS(ramTCSC,busSVC,ramUPFC)


prec={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.01,"SMP":0.01,"SMP":0.01,"SMV":0.01,"PSEUDO":0.01,"VIRTUAL":0.01,"PMU_If":0.005,"PMU_Iinj":0.005,"PMUs_V":0.005}


#%%
dfDMEDsr=create_DMED(sys,prec,graph,ram)


prec_PMUs=0.007
prec_SCADAc=0.01

#%%

dfDMED=insert_res(dfDMEDsr)

#%%

dfDMEDSCADA=dfDMED[(dfDMED["prec"]>prec_PMUs)]


#%%

dfDMEDPMU=dfDMED[(dfDMED["prec"]<prec_SCADAc)]

#%%

TCSCini=-0.15
Bini=0.4
V_sh_ini=1.1
t_sh_ini=0
V_se_ini=0.05
t_se_ini=-170*np.pi/180



for key ,tcsc in ramTCSC.items():
    tcsc.xtcsc_ini=TCSCini
for key,svc in busSVC.items():
    svc.Bini=Bini
for key,upfc in ramUPFC.items():
    upfc.Vsh_ini=V_sh_ini
    upfc.tsh_ini=t_sh_ini
    upfc.Vse_ini=V_se_ini
    upfc.tse_ini=t_se_ini




#%%
conv_WLS_SCADA,nits_WLS_SCADA,dfITsWLS_SCADA=SS_WLS_FACTS_noBC(graph,dfDMEDSCADA,ind_i,flatstart=2,printits=1,tol2=1e-1,tol=1e-4,prec_virtual=1e-4)


#%%
priori=calc_priori(graph,dfDMEDSCADA,dfDMEDPMU,ind_i)

#%%

conv_MAP,nits_MAP,dfITsMAP=SS_MAP_FACTS_withBC(graph,priori,dfDMEDPMU,ind_i,tol2=7,tol=1e-4,flatstart=1,prec_virtual=1e-4,printits=1)
# %%

conv_noWLS,nits_noWLS,dfITsWLS=SS_WLS_FACTS_noBC(graph,dfDMED,ind_i,flatstart=2,printits=1,tol2=1e-1,tol=1e-4,prec_virtual=1e-4)

# %%



fig, ax = plt.subplots(nrows=1,ncols=1,figsize=(6,4))

fig.tight_layout()


ax.set_ylim([1e-7,2])


ax.set_xticks(range(0,10))


ax.set_xlim([0,9])

ax.grid()

ax.set_title("Convergence charcateristics")

ax.set_xlabel("Iteration")
ax.set_ylabel(r"$\vert \vert \Delta x \vert \vert$")

ax.semilogy(dfITsWLS_SCADA.index,dfITsWLS_SCADA["dx"],marker='d',label="MAP SCADA")
ax.semilogy(dfITsMAP.index,dfITsMAP["dx"],marker='o',label="MAP PMU")
ax.semilogy(dfITsWLS.index,dfITsWLS["dx"],marker='x',label="WLS SCADA+PMU")
ax.legend()
# %%
