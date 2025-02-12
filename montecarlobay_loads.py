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


def modifica_cargas(dfDBAR,barras_mod,namostras_PMUs,per=0.01,seed=100):
    np.random.seed(seed)
    dfDBARs={}
    for amostra in range(namostras_PMUs):
        dfDBARs[amostra]=dfDBAR.copy()
        for barra in barras_mod:
            mask=dfDBARs[amostra]["id"]==barra

            sigmap=np.abs(dfDBARs[amostra].loc[mask,"Pd"].values[0]*per)
            sigmaq=np.abs(dfDBARs[amostra].loc[mask,"Qd"].values[0]*per)

            up=np.random.normal(0,sigmap)
            uq=np.random.normal(0,sigmaq)
            if  up > 2.5*sigmap:
                up=2.5*sigmap
            elif up < -2.5*sigmap:
                up=-2.5*sigmap

            if  uq > 2.5*sigmaq:
                uq=2.5*sigmaq
            elif uq < -2.5*sigmaq:
                uq=-2.5*sigmaq
            dfDBARs[amostra].loc[mask,"Pd"]=dfDBARs[amostra].loc[mask,"Pd"]+up
            dfDBARs[amostra].loc[mask,"Qd"]=dfDBARs[amostra].loc[mask,"Qd"]+uq
    return dfDBARs


def modifica_cargas_2(dfDBAR,barras_mod,namostras_PMUs,per=0.01,seed=100):
    np.random.seed(seed)
    dfDBARs={}
    for amostra in range(namostras_PMUs):
        if amostra==0:
            dfDBARs[amostra]=dfDBAR.copy()
        else:
            dfDBARs[amostra]=dfDBARs[amostra-1].copy()

        for barra in barras_mod:
            mask=dfDBARs[amostra]["id"]==barra

            sigmap=np.abs(dfDBARs[amostra].loc[mask,"Pd"].values[0]*per)
            sigmaq=np.abs(dfDBARs[amostra].loc[mask,"Qd"].values[0]*per)

            up=np.random.normal(0,sigmap)
            uq=np.random.normal(0,sigmaq)
            if  up > 2.5*sigmap:
                up=2.5*sigmap
            elif up < -2.5*sigmap:
                up=-2.5*sigmap

            if  uq > 2.5*sigmaq:
                uq=2.5*sigmaq
            elif uq < -2.5*sigmaq:
                uq=-2.5*sigmaq
            dfDBARs[amostra].loc[mask,"Pd"]=dfDBARs[amostra].loc[mask,"Pd"]+up
            dfDBARs[amostra].loc[mask,"Qd"]=dfDBARs[amostra].loc[mask,"Qd"]+uq
    return dfDBARs


def cria_setpoint_FACTS(graph,ramTCSC,busSVC,ramUPFC,namostras_PMUs,pertcsc,persvc,perupfc_psp,perupfc_qsp,perupfc_vp):
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
    
    TCSCs=ramTCSC.keys()
    SVCs=dfsvc_original_values.keys()
    UPFCs=dfUPFC_original_values.keys()
    tcsc_setpoint={}
    svc_setpoint={}
    upfcs_Psp_setpoint={}
    upfcs_Qsp_setpoint={}
    upfcs_Vp_setpoint={}

    for key in TCSCs:
        tcsc_setpoint[key]=[]
        for sample in range(namostras_PMUs):
            tcsc_setpoint[key].append(dfTCSC_original_values[key]*(1+pertcsc/100))
    for key in SVCs:
        svc_setpoint[key]=[]
        for sample in range(namostras_PMUs):
            svc_setpoint[key].append(dfsvc_original_values[key]*(1+persvc/100))
    for key in UPFCs:
        upfcs_Psp_setpoint[key]=[]
        upfcs_Qsp_setpoint[key]=[]
        upfcs_Vp_setpoint[key]=[]
        for sample in range(namostras_PMUs):
            upfcs_Psp_setpoint[key].append(dfUPFC_original_values[key]["Psp"]*(1+perupfc_psp/100))
            upfcs_Qsp_setpoint[key].append(dfUPFC_original_values[key]["Qsp"]*(1+perupfc_qsp/100))
            upfcs_Vp_setpoint[key].append(dfUPFC_original_values[key]["Vp"]*(1+perupfc_vp/100))
    
    return tcsc_setpoint,svc_setpoint,upfcs_Psp_setpoint,upfcs_Qsp_setpoint,upfcs_Vp_setpoint


            


#%% Lê arquivos e constroi a estrutura da rede

sys="IEEE14_rakp2009"
measFACTS=False
nome="loadvar4"

if measFACTS==True: #nomeclatura dos arquivos de entrada
    Meas="ComMedidas"
else:
    Meas="SemMedidas"



dfDBAR,dfDBRAN,dfDMED,dfDFACTS=read_files(sys) # lê arquivos


[bars,nbars,pv,pq,ind_i]=creat_bar(dfDBAR)
[ram,nbran]=create_bran(dfDBRAN,ind_i)

[ramTCSC,nbranTCSC]=create_TCSC(dfDFACTS,ind_i)

[busSVC,BUS_SVC]=create_SVC(dfDFACTS,ind_i)

[ramUPFC,nbranUPFC]=create_UPFC(dfDFACTS,ind_i)

graph=create_graph(bars,ram)

addTCSCingraph(graph,ramTCSC)

addSVCingraph(graph,busSVC)

addUPFCingraph(graph,ramUPFC)


#%% Guarda os Set points originais do ramo, para calcular o percentual em relação a eles



#casos de compensação
#tempo de simulação em segundos
#%%
t=6
ts_SCADA=2
ts_PMU=0.1

namostras_PMUs=int(t/ts_PMU)
#%%
namostras_SCADA=int(t/ts_SCADA)
#%%

dfcasos=pd.DataFrame(data={"TCSC":[-15],"SVC":[1],"UPFC_flow":[10],"UPFC_V":[2],"TCSC_ini":[-0.05],"SVC_ini":[0.10]})
#%%



#%%
barras_mod=[4,5,12]
per=0.01



dfDBARs=modifica_cargas_2(dfDBAR,barras_mod,namostras_PMUs,per,seed=10)
#%%
#%%
#cria_setpointsFACTS

pertcsc=5
persvc=1
perupfc_psp=5
perupfc_qsp=5
perupfc_vp=1



[tcsc_setpoint,svc_setpoint,upfcs_Psp_setpoint,upfcs_Qsp_setpoint,upfcs_Vp_setpoint]=cria_setpoint_FACTS(graph,ramTCSC,busSVC,ramUPFC,namostras_PMUs,pertcsc,persvc,perupfc_psp,perupfc_qsp,perupfc_vp)

#%%

lst=["1-14"]
s=25
for item in lst:
    for i in range(25,namostras_PMUs):
        tcsc_setpoint[item][i]=tcsc_setpoint[item][i]*1.10





xtcsc_ini=-0.01
svc_ini=0.1


#%%

dDMEDfps={}
dState_ref={}
dStateTCSC_ref={}
amostras_convergidas=0
for amostra in range(namostras_PMUs):
    for key ,tcsc in ramTCSC.items():
        tcsc.Pfesp=tcsc_setpoint[key][amostra]
        tcsc.xtcsc_ini=xtcsc_ini
    for key,svc in busSVC.items():
        graph[key].bar.V=svc_setpoint[key][amostra]
        svc.Bini=svc_ini
    for key,upfc in ramUPFC.items():
        upfc.Psp_set=upfcs_Psp_setpoint[key][amostra]
        upfc.Qsp_set=upfcs_Qsp_setpoint[key][amostra]
        graph[upfc.p].bar.V=upfcs_Vp_setpoint[key][amostra]
    
    for idx,barra in dfDBARs[amostra].iterrows():
        k=ind_i[int(barra.id)]
        graph[k].bar.Pd=barra["Pd"]/100
        graph[k].bar.Qd=barra["Qd"]/100

    try:    
        conv=load_flow_FACTS(graph,inici=1,prt=1,itmax=20,printgrad=0,printres=0)
    except:
        conv=0
    
    #get states and 
    if conv==1:
        amostras_convergidas=amostras_convergidas+1
        ram.update(ramTCSC)
        dDMEDfps[amostra]=save_DMED_fp(graph,ram,sys,ramUPFC)
        dState_ref[amostra]=get_state(graph)
        dStateTCSC_ref[amostra]=get_state_FACTS(ramTCSC,busSVC,ramUPFC)

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

dfSATES_ref.to_csv("ResultadosPowerTech/state_ref"+sys+nome+".csv")
dfSATES_FACTS_ref.to_csv("ResultadosPowerTech/state_FACTS_ref"+sys+nome+".csv")

#%%


if measFACTS==True:
    dfDMEDs={}
    for ts in range(namostras_PMUs):
        prec={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.01,"SMP":0.01,"SMP":0.01,"SMV":0.01,"PSEUDO":0.01,"VIRTUAL":0.01,"PMU_If":0.005,"PMU_Iinj":0.005,"PMUs_V":0.005}
        dfDMED=create_DMED(sys,prec,graph,ram,ramUPFC,dfDMEDfp=dDMEDfps[ts])
        dfDMEDFACTs=create_DMED_FACTS(sys,prec,graph,ram,ramUPFC,dfDMEDfp=dDMEDfps[idx])
        dfDMEDsr=pd.concat([dfDMED.copy(),dfDMEDFACTs.copy()])
        dfDMEDs[ts]=dfDMEDsr.copy()
else:
    dfDMEDs={}
    for ts in range(namostras_PMUs):
        prec={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.01,"SMP":0.05,"SMV":0.03,"PSEUDO":0.3,"VIRTUAL":1e-5,"TCSCvar":0.01,"SVCvar":0.01,"UPFCt_sh":0.01,"UPFCV_sh":0.01,"UPFCt_se":0.01,"UPFCV_se":0.01,"PMU_If":0.001,"PMU_Iinj":0.001,"PMUs_V":0.001}
        dfDMED=create_DMED(sys,prec,graph,ram,ramUPFC,dfDMEDfp=dDMEDfps[ts])
        dfDMEDs[ts]=dfDMED.copy()


prec_LIM=0.007


#%%
TCSCini=-0.01
Bini=0.1
V_sh_ini=1.0
t_sh_ini=0
V_se_ini=0.05
t_se_ini=-120*np.pi/180
cx="x1"

dconv_MAP_SCADA={}
dconv_MAP_PMU={}
dconv_WLS={}
dnits_MAP_SCADA={}
dnits_MAP_PMU={}
dnits_WLS={}
N=1

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


for ts in range(namostras_PMUs):
    dconv_MAP_SCADA[ts]=[]
    dconv_MAP_PMU[ts]=[]
    dconv_WLS[ts]=[]
    dnits_MAP_SCADA[ts]=[]
    dnits_MAP_PMU[ts]=[]
    dnits_WLS[ts]=[]
    dState_MAP_SCADA[ts]=[]
    dStateFACTS_MAP_SCADA[ts]=[]
    dState_MAP_PMU[ts]=[]
    dStateFACTS_MAP_PMU[ts]=[]
    dState_WLS[ts]=[]
    dStateFACTS_WLS[ts]=[]


    dfDMEDatual=dfDMEDs[ts].copy()
    # dfDEMEDruido=insert_res(dfDMEDatual,n)

    if (ts/10) % 2 ==0:
        dfDMEDSCADA=dfDMEDatual[(dfDMEDatual["prec"]>prec_LIM)].copy()
    dfDMEDPMU=dfDMEDatual[(dfDMEDatual["prec"]<prec_LIM)].copy()



    for n in range(N): 

        dfDMED_SCADAn=insert_res(dfDMEDSCADA,n)
        dfDMED_PMUn=insert_res(dfDMEDPMU,n)

        dfDMED_WLSn=pd.concat([dfDMED_SCADAn,dfDMED_PMUn])

        for key ,tcsc in ramTCSC.items():
            tcsc.xtcsc_ini=TCSCini
        for key,svc in busSVC.items():
            svc.Bini=Bini

        for key,upfc in ramUPFC.items():
            upfc.Vsh_ini=V_sh_ini
            upfc.tsh_ini=t_sh_ini
            upfc.Vse_ini=V_se_ini
            upfc.tse_ini=t_se_ini

              
        conv_WLS,nits_WLS,dfITsWLS=SS_WLS_FACTS_noBC(graph,dfDMED_WLSn,ind_i,printgrad=0,printres=1,printits=2,flatstart=2,tol=1e-6,tol2=1e-1)


        
        if conv_WLS==True:
            dState_WLS[ts].append(get_state(graph,n))
            dStateFACTS_WLS[ts].append(get_state_FACTS(ramTCSC,busSVC,ramUPFC,n))
        
        conv_MAP_SCADA,nits_MAP_SCADA,dfITsMAP_SCADA=SS_WLS_FACTS_noBC(graph,dfDMED_SCADAn,ind_i,flatstart=2,printres=0,printits=2,tol2=1e-1,tol=1e-6)
        

        if conv_MAP_SCADA==True:
            dState_MAP_SCADA[ts].append(get_state(graph,n))
            dStateFACTS_MAP_SCADA[ts].append(get_state_FACTS(ramTCSC,busSVC,ramUPFC,n))

        if conv_MAP_SCADA==True:
            priori=calc_priori(graph,dfDMED_SCADAn,dfDMED_PMUn,ind_i)
            conv_MAP_PMU,nits_MAP_PMU,dfITsMAP_PMU=SS_MAP_FACTS_withBC(graph,priori,dfDMED_PMUn,ind_i,tol2=7,tol=1e-6,flatstart=1,printres=1,printits=2)
        else:
            conv_MAP_PMU=0
            nits_MAP_PMU=30
            dfITsMAP_PMU=pd.DataFrame()
            
        if conv_MAP_PMU==True:
            dState_MAP_PMU[ts].append(get_state(graph,n))
            dStateFACTS_MAP_PMU[ts].append(get_state_FACTS(ramTCSC,busSVC,ramUPFC,n))



   

        
        dconv_WLS[ts].append(conv_WLS)
        dconv_MAP_SCADA[ts].append(conv_MAP_SCADA)
        dconv_MAP_PMU[ts].append(conv_MAP_PMU)
        dnits_WLS[ts].append(nits_WLS)
        dnits_MAP_SCADA[ts].append(nits_MAP_SCADA)
        dnits_MAP_PMU[ts].append(nits_MAP_PMU)

        dconv["n"].append(n)
        dconv["convMAP_SCADA"].append(conv_MAP_SCADA)
        dconv["convMAP_PMU"].append(conv_MAP_PMU)
        dconv["convWLS"].append(conv_WLS)
        dconv["nitsMAP_SCADA"].append(nits_MAP_SCADA)
        dconv["nitsMAP_PMU"].append(nits_MAP_PMU)
        dconv["nitsWLS"].append(nits_WLS)
        dconv["caso"].append(ts)

        if not dfITsMAP_SCADA.empty:
            dfITsMAP_SCADA["method"]="MAP_SCADA"
            dfITsMAP_SCADA["caso"]=ts
            dfITsMAP_SCADA["n"]=n
        if not dfITsMAP_PMU.empty:
            dfITsMAP_PMU["method"]="MAP_PMUs"
            dfITsMAP_PMU["caso"]=ts
            dfITsMAP_PMU["n"]=n
        if not dfITsWLS.empty:
            dfITsWLS["method"]="WLS"
            dfITsWLS["caso"]=ts
            dfITsWLS["n"]=n
        dfITS=pd.concat([dfITS,dfITsMAP_SCADA,dfITsMAP_PMU,dfITsWLS])
#%%        
dfConvs=pd.DataFrame(dconv)
# %%


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
dfconv.to_csv("ResultadosPowerTech/resultados_conv_"+sys+str(cx)+Meas+nome+".csv")
#%%
dfSATES.to_csv("ResultadosPowerTech/state_"+sys+str(cx)+Meas+nome+".csv")
dfSATES_FACTS.to_csv("ResultadosPowerTech/state_FACTS_"+sys+str(cx)+Meas+nome+".csv")
#%%