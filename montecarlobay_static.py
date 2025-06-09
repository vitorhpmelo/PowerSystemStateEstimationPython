#%% Simulações de monte carlo
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


#%% Lê arquivos e constroi a estrutura da rede

sys="IEEE14_rakp2009"
measFACTS=False

if measFACTS==True: #nomeclatura dos arquivos de entrada
    Meas="ComMedidas"
else:
    Meas="SemMedidas"



dfDBAR,dfDBRAN,dfDMED,dfDFACTS=read_files(sys) # lê arquivos


[bars,nbars,pv,pq,ind_i]=creat_bus(dfDBAR)
[ram,nbran]=create_bran(dfDBRAN,ind_i)

[ramTCSC,nbranTCSC]=create_TCSC(dfDFACTS,ind_i)

[busSVC,BUS_SVC]=create_SVC(dfDFACTS,ind_i)

[ramUPFC,nbranUPFC]=create_UPFC(dfDFACTS,ind_i)

graph=create_graph(bars,ram)

addTCSCingraph(graph,ramTCSC)

addSVCingraph(graph,busSVC)

addUPFCingraph(graph,ramUPFC)


#%% Guarda os Set points originais do ramo, para calcular o percentual em relação a eles

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
        

#casos de compensação

dfcasos=pd.DataFrame(data={"TCSC":[10],"SVC":[1],"UPFC_flow":[-10],"UPFC_V":[1],"TCSC_ini":[-0.05],"SVC_ini":[0.10]})
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
        upfc.Qsp_set=dfUPFC_original_values[key]["Qsp"]*(1+(row["UPFC_flow"]/100))
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

#%%
dfSATES_ref=pd.DataFrame() #salva os valores de referência das variáveis de estado normais
dfSATES_FACTS_ref=pd.DataFrame() #salva os valores de referência das variáveis de estado dos FACTS

for key,item in dState_ref.items():
    df=item
    df["method"]="PF"
    df["scenario"]=key
    dfSATES_ref=pd.concat([dfSATES_ref,df])
    
for key,item in dStateTCSC_ref.items():
    df=item
    df["method"]="PF"
    df["scenario"]=key
    dfSATES_FACTS_ref=pd.concat([dfSATES_FACTS_ref,df])
#%%
dfSATES_ref.to_csv("ResultadosISGT/state_ref"+sys+".csv")
dfSATES_FACTS_ref.to_csv("ResultadosISGT/state_FACTS_ref"+sys+".csv")

#%%


if measFACTS==True:
    dfDMEDs={}
    for idx, row in dfcasos.iterrows():
        prec={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.01,"SMP":0.01,"SMP":0.01,"SMV":0.01,"PSEUDO":0.01,"VIRTUAL":0.01,"PMU_If":0.005,"PMU_Iinj":0.005,"PMUs_V":0.005}
        dfDMED=create_DMED(sys,prec,graph,ram,ramUPFC,dfDMEDfp=dDMEDfps[idx])
        dfDMEDFACTs=create_DMED_FACTS(sys,prec,graph,ram,ramUPFC,dfDMEDfp=dDMEDfps[idx])
        dfDMEDsr=pd.concat([dfDMED.copy(),dfDMEDFACTs.copy()])
        dfDMEDs[idx]=dfDMEDsr.copy()
else:
    dfDMEDs={}
    for idx, row in dfcasos.iterrows():
        prec={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.01,"SMP":0.05,"SMV":0.03,"PSEUDO":0.3,"VIRTUAL":1e-5,"TCSCvar":0.01,"SVCvar":0.01,"UPFCt_sh":0.01,"UPFCV_sh":0.01,"UPFCt_se":0.01,"UPFCV_se":0.01}
        dfDMED=create_DMED(sys,prec,graph,ram,ramUPFC,dfDMEDfp=dDMEDfps[idx])
        dfDMEDs[idx]=dfDMED.copy()


prec_LIM=0.005


#%%
TCSCini=-0.1
Bini=0.4
V_sh_ini=1.0
t_sh_ini=0
V_se_ini=0.05
t_se_ini=-90*np.pi/180
cx="x1"
dfini_SE={"TCSC_ini":[TCSCini,TCSCini,TCSCini,TCSCini],"SVC_ini":[Bini,Bini,Bini,Bini],
         "UPFC_Vsh":[V_sh_ini,V_sh_ini,V_sh_ini,V_sh_ini],"UPFC_tsh":[t_sh_ini,t_sh_ini,t_sh_ini,t_sh_ini],
         "UPFC_Vse":[V_se_ini,V_se_ini,V_se_ini,V_se_ini],"UPFC_tse":[t_se_ini,t_se_ini,t_se_ini,t_se_ini]
         }
dconv_MAP_SCADA={}
dconv_MAP_PMU={}
dconv_WLS={}
dnits_MAP_SCADA={}
dnits_MAP_PMU={}
dnits_WLS={}
N=100

dState_MAP_SCADA={}
dStateFACTS_MAP_SCADA={}
dState_MAP_PMU={}
dStateFACTS_MAP_PMU={}
dState_WLS={}
dStateFACTS_WLS={}
dfITS=pd.DataFrame()
dconv={}
dconv["n"]=[]
dconv["convMAP_SCADA"]=[]
dconv["convMAP_PMU"]=[]
dconv["convWLS"]=[]
dconv["nitsMAP_SCADA"]=[]
dconv["nitsMAP_PMU"]=[]
dconv["nitsWLS"]=[]
dconv["caso"]=[]


for idx, row in dfcasos.iterrows():
    dconv_MAP_SCADA[idx]=[]
    dconv_MAP_PMU[idx]=[]
    dconv_WLS[idx]=[]
    dnits_MAP_SCADA[idx]=[]
    dnits_MAP_PMU[idx]=[]
    dnits_WLS[idx]=[]
    dState_MAP_SCADA[idx]=[]
    dStateFACTS_MAP_SCADA[idx]=[]
    dState_MAP_PMU[idx]=[]
    dStateFACTS_MAP_PMU[idx]=[]
    dState_WLS[idx]=[]
    dStateFACTS_WLS[idx]=[]


    for n in range(N): 
        dfDMED=insert_res(dfDMEDs[idx],n)


        dfDMEDSCADA=dfDMED[(dfDMED["prec"]>prec_LIM)].copy()

        dfDMEDPMU=dfDMED[(dfDMED["prec"]<prec_LIM)].copy()


        for key ,tcsc in ramTCSC.items():

            tcsc.xtcsc_ini=dfini_SE["TCSC_ini"][idx]
        for key,svc in busSVC.items():
            svc.Bini=dfini_SE["SVC_ini"][idx]

        for key,upfc in ramUPFC.items():
            upfc.Vsh_ini=dfini_SE["UPFC_Vsh"][idx]
            upfc.tsh_ini=dfini_SE["UPFC_tsh"][idx]
            upfc.Vse_ini=dfini_SE["UPFC_Vse"][idx]
            upfc.tse_ini=dfini_SE["UPFC_tse"][idx]
     
        conv_WLS,nits_WLS,dfITsWLS=SS_WLS_FACTS_noBC(graph,dfDMED,ind_i,printgrad=0,printres=0,printits=1,flatstart=2,tol=1e-5,tol2=1e-4)


        
        if conv_WLS==True:
            dState_WLS[idx].append(get_state(graph,n))
            dStateFACTS_WLS[idx].append(get_state_FACTS(ramTCSC,busSVC,ramUPFC,n))
        
        conv_MAP_SCADA,nits_MAP_SCADA,dfITsMAP_SCADA=SS_WLS_FACTS_noBC(graph,dfDMEDSCADA,ind_i,flatstart=2,printits=1,tol2=1e-1,tol=1e-4,prec_virtual=1e-4)
        
        if conv_MAP_SCADA==True:
            dState_MAP_SCADA[idx].append(get_state(graph,n))
            dStateFACTS_MAP_SCADA[idx].append(get_state_FACTS(ramTCSC,busSVC,ramUPFC,n))

        if conv_MAP_SCADA==True:
            priori=calc_priori(graph,dfDMEDSCADA,dfDMEDPMU,ind_i)
            conv_MAP_PMU,nits_MAP_PMU,dfITsMAP_PMU=SS_MAP_FACTS_withBC(graph,priori,dfDMEDPMU,ind_i,tol2=7,tol=1e-4,flatstart=1,prec_virtual=1e-4,printits=1)
        else:
            conv_MAP_PMU=0
            nits_MAP_PMU=30
            dfITsMAP_PMU=pd.DataFrame()
            
        if conv_MAP_PMU==True:
            dState_MAP_PMU[idx].append(get_state(graph,n))
            dStateFACTS_MAP_PMU[idx].append(get_state_FACTS(ramTCSC,busSVC,ramUPFC,n))

        
        dconv_WLS[idx].append(conv_WLS)
        dconv_MAP_SCADA[idx].append(conv_MAP_SCADA)
        dconv_MAP_PMU[idx].append(conv_MAP_PMU)
        dnits_WLS[idx].append(nits_WLS)
        dnits_MAP_SCADA[idx].append(nits_MAP_SCADA)
        dnits_MAP_PMU[idx].append(nits_MAP_PMU)

        dconv["n"].append(n)
        dconv["convMAP_SCADA"].append(conv_MAP_SCADA)
        dconv["convMAP_PMU"].append(conv_MAP_PMU)
        dconv["convWLS"].append(conv_WLS)
        dconv["nitsMAP_SCADA"].append(nits_MAP_SCADA)
        dconv["nitsMAP_PMU"].append(nits_MAP_PMU)
        dconv["nitsWLS"].append(nits_WLS)
        dconv["caso"].append(idx)

        if not dfITsMAP_SCADA.empty:
            dfITsMAP_SCADA["method"]="MAP_SCADA"
            dfITsMAP_SCADA["caso"]=idx
            dfITsMAP_SCADA["n"]=n
        if not dfITsMAP_PMU.empty:
            dfITsMAP_PMU["method"]="MAP_PMUs"
            dfITsMAP_PMU["caso"]=idx
            dfITsMAP_PMU["n"]=n
        if not dfITsWLS.empty:
            dfITsWLS["method"]="WLS"
            dfITsWLS["caso"]=idx
            dfITsWLS["n"]=n
        dfITS=pd.concat([dfITS,dfITsMAP_SCADA,dfITsMAP_PMU,dfITsWLS])
#%%        
dfConvs=pd.DataFrame(dconv)
# %%
print("Nconvs WLS")
print(sum(dfConvs["convWLS"]))
print("Nconvs MAP SACADA")
print(sum(dfConvs["convMAP_SCADA"]))
print("Nconvs MAP PMUs")
print(sum(dfConvs["convMAP_PMU"]))

#%%

dfSATES=pd.DataFrame()
dfSATES_FACTS=pd.DataFrame()


#%%


for key,item in dState_WLS.items():
    if len(item)>0:
        df=pd.concat(item)
        df["method"]="WLS"
        df["scenario"]=key
        
        dfSATES=pd.concat([dfSATES,df])
        
for key,item in dStateFACTS_WLS.items():
    if len(item)>0:
        df=pd.concat(item)
        df["method"]="WLS"
        df["scenario"]=key
        dfSATES_FACTS=pd.concat([dfSATES_FACTS,df])

for key,item in dState_MAP_SCADA.items():
    if len(item)>0:
        df=pd.concat(item)
        df["method"]="MAP_SCADA"
        df["scenario"]=key
        
        dfSATES=pd.concat([dfSATES,df])

for key,item in dStateFACTS_MAP_SCADA.items():
    if len(item)>0:
        df=pd.concat(item)
        df["method"]="MAP_SCADA"
        df["scenario"]=key
        dfSATES_FACTS=pd.concat([dfSATES_FACTS,df])


for key,item in dState_MAP_PMU.items():
    if len(item)>0:
        df=pd.concat(item)
        df["method"]="MAP_PMU"
        df["scenario"]=key
        dfSATES=pd.concat([dfSATES,df])


for key,item in dStateFACTS_MAP_PMU.items():
    if len(item)>0:
        df=pd.concat(item)
        df["method"]="MAP_PMU"
        df["scenario"]=key
        dfSATES_FACTS=pd.concat([dfSATES_FACTS,df])



#%%
dfconv=pd.DataFrame(data=dconv)
dfconv.to_csv("ResultadosISGT/resultados_conv_"+sys+str(cx)+Meas+".csv")
#%%
dfSATES.to_csv("ResultadosISGT/state_"+sys+str(cx)+Meas+".csv")
dfSATES_FACTS.to_csv("ResultadosISGT/state_FACTS_"+sys+str(cx)+Meas+".csv")
#%%