#%% Simulações de monte carlo
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#versao com amostragem assincrona entre SCADA e PMU

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
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt



def modifica_cargas_aleatorio(dfDBAR,barras_mod,n_simulacoes,per=0.01,seed=100):
    #modifica carga em um lista de barras relação ao último instante de temopo 
    rng=np.random.RandomState(seed)
    dfDBARs={}
    for amostra in range(n_simulacoes):
        if amostra==0:
            dfDBARs[amostra]=dfDBAR.copy()
        else:
            dfDBARs[amostra]=dfDBARs[amostra-1].copy()

        for barra in barras_mod:
            mask=dfDBARs[amostra]["id"]==barra

            sigmap=np.abs(dfDBARs[amostra].loc[mask,"Pd"].values[0]*per)
            sigmaq=np.abs(dfDBARs[amostra].loc[mask,"Qd"].values[0]*per)

            up=rng.normal(0,sigmap)
            uq=rng.normal(0,sigmaq)
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

def modifica_cargas_rampa(dfDBAR,barras_mod,namostras_PMUs,amostra_ini,delta,perP=0.01,perQ=0.01):
    #modifica carga em um lista de barras relação ao último instante de temopo 
    
    dfDBARs={}



    for amostra in range(namostras_PMUs):
        if amostra==0:
            dfDBARs[amostra]=dfDBAR.copy()
        else:
            dfDBARs[amostra]=dfDBARs[amostra-1].copy()

        if (amostra > amostra_ini)& (amostra <= amostra_ini+delta):

            for barra in barras_mod:
                mask=dfDBARs[amostra]["id"]==barra

                deltap=np.abs(dfDBARs[amostra_ini].loc[mask,"Pd"].values[0]*perP)/delta
                deltaq=np.abs(dfDBARs[amostra_ini].loc[mask,"Qd"].values[0]*perQ)/delta

                dfDBARs[amostra].loc[mask,"Pd"]=dfDBARs[amostra-1].loc[mask,"Pd"]+deltap
                dfDBARs[amostra].loc[mask,"Qd"]=dfDBARs[amostra-1].loc[mask,"Qd"]+deltaq


    return dfDBARs

def modifica_cargas_rampa_existente(dfDBARs,barras_mod,namostras_PMUs,amostra_ini,delta,perP=0.01,perQ=0.01):
    #modifica carga em um lista de barras relação ao último instante de temopo 


    for amostra in range(namostras_PMUs):

        
    
        if (amostra > amostra_ini)& (amostra <= amostra_ini+delta):

            for barra in barras_mod:
                mask=dfDBARs[amostra]["id"]==barra

                deltap=np.abs(dfDBARs[amostra_ini].loc[mask,"Pd"].values[0]*perP)/delta
                deltaq=np.abs(dfDBARs[amostra_ini].loc[mask,"Qd"].values[0]*perQ)/delta

                dfDBARs[amostra].loc[mask,"Pd"]=dfDBARs[amostra-1].loc[mask,"Pd"]+deltap
                dfDBARs[amostra].loc[mask,"Qd"]=dfDBARs[amostra-1].loc[mask,"Qd"]+deltaq


    return dfDBARs

def cria_setpoint_FACTS(graph,ramTCSC,busSVC,ramUPFC,namostras,pertcsc,persvc,perupfc_psp,perupfc_qsp,perupfc_vp):
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
        for sample in range(namostras):
            tcsc_setpoint[key].append(dfTCSC_original_values[key]*(1+pertcsc/100))
    for key in SVCs:
        svc_setpoint[key]=[]
        for sample in range(namostras):
            svc_setpoint[key].append(dfsvc_original_values[key]*(1+persvc/100))
    for key in UPFCs:
        upfcs_Psp_setpoint[key]=[]
        upfcs_Qsp_setpoint[key]=[]
        upfcs_Vp_setpoint[key]=[]
        for sample in range(namostras):
            upfcs_Psp_setpoint[key].append(dfUPFC_original_values[key]["Psp"]*(1+perupfc_psp/100))
            upfcs_Qsp_setpoint[key].append(dfUPFC_original_values[key]["Qsp"]*(1+perupfc_qsp/100))
            upfcs_Vp_setpoint[key].append(dfUPFC_original_values[key]["Vp"]*(1+perupfc_vp/100))
    
    return tcsc_setpoint,svc_setpoint,upfcs_Psp_setpoint,upfcs_Qsp_setpoint,upfcs_Vp_setpoint

def get_var_loads(dfDBARs,n_simulacoes,barras_mod):
    dloadsP={}
    dloadsQ={}
    for bar in barras_mod:
        dloadsP[bar]=[]
        dloadsQ[bar]=[]

    for i in range(n_simulacoes):
        for bar in barras_mod:
            dloadsP[bar].append(dfDBARs[i].loc[dfDBARs[i]["id"]==bar,"Pd"].values[0])
            dloadsQ[bar].append(dfDBARs[i].loc[dfDBARs[i]["id"]==bar,"Qd"].values[0])
    return dloadsP,dloadsQ

#%% Lê arquivos e constroi a estrutura da rede

sys="IEEE14_rakp2009"
measFACTS=False
file="SE_data/"
nome="loadvar_sudden3"
lamb=0.001

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


#casos de compensação
#tempo de simulação em segundos
#%%
t=8
ts_SCADA=2
ts_PMU=0.1
ts_simu=0.1/2



namostras_PMUs=int(t/ts_PMU)
#%%
namostras_SCADA=int(t/ts_SCADA)

n_simulacoes=int(t/(ts_simu))
#%%

dfcasos=pd.DataFrame(data={"TCSC":[-15],"SVC":[1],"UPFC_flow":[10],"UPFC_V":[2],"TCSC_ini":[-0.05],"SVC_ini":[0.10]})
#%%



#%%

per=0.005

barras_mod=[3,
4,
5,
6,
9,
10,
11,
12,
13,
14]

dfDBARs=modifica_cargas_aleatorio(dfDBAR,barras_mod,n_simulacoes,per,seed=10) #loads and facts


# dfDBARs=modifica_cargas_aleatorio(dfDBAR,barras_mod,n_simulacoes,per,seed=160) #loads var only

#%%

barras_mod=[4]
amostrain=1.5/ts_simu
delta=2
dfDBARs=modifica_cargas_rampa_existente(dfDBARs,barras_mod,n_simulacoes,amostra_ini=amostrain,delta=delta,perP=0.10,perQ=0.10)
#%%
#%%
loads_P,loads_Q=get_var_loads(dfDBARs,n_simulacoes,[5])

plt.plot(loads_P[5])
#%%
# plt.ylim(ymin=44,ymax=51)
#%%
#cria_setpointsFACTS

pertcsc=5
persvc=1
perupfc_psp=5
perupfc_qsp=5
perupfc_vp=1



[tcsc_setpoint,svc_setpoint,upfcs_Psp_setpoint,upfcs_Qsp_setpoint,upfcs_Vp_setpoint]=cria_setpoint_FACTS(graph,ramTCSC,busSVC,ramUPFC,n_simulacoes,pertcsc,persvc,perupfc_psp,perupfc_qsp,perupfc_vp)

#%%




for i in range(2*35,2*80): 
    svc_setpoint[2][i]=svc_setpoint[2][i]*1.02


for i in range(2*50,2*80): 
    tcsc_setpoint["1-14"][i]=tcsc_setpoint["1-14"][i]*1.02


for i in range(2*70,2*80):
    upfcs_Vp_setpoint["5-15"][i]=upfcs_Vp_setpoint["5-15"][i]*1.02
    


xtcsc_ini=-0.01
svc_ini=0.1


#%%

dDMEDfps={}
dState_ref={}
dStateFACTS_ref={}
amostras_convergidas=0
for amostra in range(n_simulacoes):
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
        dStateFACTS_ref[amostra]=get_state_FACTS(ramTCSC,busSVC,ramUPFC)

#%%
dfSATES_ref=pd.DataFrame() #salva os valores de referência das variáveis de estado normais
dfSATES_FACTS_ref=pd.DataFrame() #salva os valores de referência das variáveis de estado dos FACTS

for key,item in dState_ref.items():
    df=item
    df["method"]="PF"
    df["scenario"]=key
    dfSATES_ref=pd.concat([dfSATES_ref,df])
    
for key,item in dStateFACTS_ref.items():
    df=item
    df["method"]="PF"
    df["scenario"]=key
    dfSATES_FACTS_ref=pd.concat([dfSATES_FACTS_ref,df])
#%%
dfSATES_ref.sort_values(by=["scenario","de","tipo"],ignore_index=True,inplace=True)
dfSATES_FACTS_ref.sort_values(by=["scenario","de","tipo"],ignore_index=True,inplace=True)

#%%


#%%


if measFACTS==True:
    dfDMEDs={}
    for ts in range(n_simulacoes):
        prec={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.01,"SMP":0.01,"SMP":0.01,"SMV":0.01,"PSEUDO":0.01,"VIRTUAL":0.01,"PMU_If":0.005,"PMU_Iinj":0.005,"PMUs_V":0.005}
        dfDMED=create_DMED(sys,prec,graph,ram,ramUPFC,dfDMEDfp=dDMEDfps[ts])
        dfDMEDFACTs=create_DMED_FACTS(sys,prec,graph,ram,ramUPFC,dfDMEDfp=dDMEDfps[ts])
        dfDMEDsr=pd.concat([dfDMED.copy(),dfDMEDFACTs.copy()])
        dfDMEDs[ts]=dfDMEDsr.copy()
else:
    dfDMEDs={}
    for ts in range(n_simulacoes):
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
#%%

amostras_PMU=np.round((np.arange(0,t,ts_PMU)+ts_simu)/ts_simu,0)
amostras_PMU=list(amostras_PMU.astype(np.int64))

amostras_SCADA=np.round((np.arange(0,t,ts_SCADA))/ts_simu,0)

amostras_SCADA=list(amostras_SCADA.astype(int))
#%%
simulacoes= amostras_PMU + amostras_SCADA
simulacoes.sort()
#%%
print("Lambda {:f}".format(lamb))

# namostras= int(ts_SCADA/ts_PMU)

# lamdas= np.linspace(0.5,0.005,namostras)

#%%
np.random.seed(1)
cont=0
for n in tqdm(range(N)): 

    for ts in simulacoes:



        dfDMEDatual=dfDMEDs[ts].copy()
        dfDEMEDruido=insert_res(dfDMEDatual)

        if ts in amostras_SCADA:
            dfDMEDSCADAn=dfDEMEDruido[(dfDEMEDruido["prec"]>prec_LIM)].copy()
            cont=0
            continue
        elif ts in amostras_PMU:
            dfDMEDPMUn=dfDEMEDruido[(dfDEMEDruido["prec"]<prec_LIM)].copy()

        # lamb=lamdas[cont]
        cont=cont+1
        if n==0:
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

        dfDMED_WLSn=pd.concat([dfDMEDSCADAn,dfDMEDPMUn])

        for key ,tcsc in ramTCSC.items():
            tcsc.xtcsc_ini=TCSCini
        for key,svc in busSVC.items():
            svc.Bini=Bini

        for key,upfc in ramUPFC.items():
            upfc.Vsh_ini=V_sh_ini
            upfc.tsh_ini=t_sh_ini
            upfc.Vse_ini=V_se_ini
            upfc.tse_ini=t_se_ini
    
        conv_WLS,nits_WLS,dfITsWLS=SS_WLS_FACTS_noBC(graph,dfDMED_WLSn,ind_i,printgrad=0,printres=0,printits=2,flatstart=2,tol=1e-6,tol2=1e-1)


        if conv_WLS==0:
            print("caso divergente")


        if conv_WLS==True:
            dState_WLS[ts].append(get_state(graph,n,df_ref=dState_ref[ts]))
            dStateFACTS_WLS[ts].append(get_state_FACTS(ramTCSC,busSVC,ramUPFC,n,df_ref=dStateFACTS_ref[ts]))
        

        conv_MAP_SCADA,nits_MAP_SCADA,dfITsMAP_SCADA=SS_WLS_FACTS_noBC(graph,dfDMEDSCADAn,ind_i,printgrad=0,flatstart=2,printres=0,printits=2,tol2=1e-1,tol=1e-6)
        
        if conv_MAP_SCADA==0:
            print("caso divergente")


        if conv_MAP_SCADA==True:
            dState_MAP_SCADA[ts].append(get_state(graph,n,df_ref=dState_ref[ts]))
            dStateFACTS_MAP_SCADA[ts].append(get_state_FACTS(ramTCSC,busSVC,ramUPFC,n,df_ref=dStateFACTS_ref[ts]))
        
        if conv_MAP_SCADA==True:
            priori=calc_priori(graph,dfDMEDSCADAn,dfDMEDPMUn,ind_i,lamb=lamb)
            conv_MAP_PMU,nits_MAP_PMU,dfITsMAP_PMU=SS_MAP_FACTS_withBC(graph,priori,dfDMEDPMUn,ind_i,tol2=7,tol=1e-6,flatstart=1,printres=0,printits=2,printgrad=0)
        else:
            print("divergencia no MAP PMU")
            conv_MAP_PMU=0
            nits_MAP_PMU=30
            dfITsMAP_PMU=pd.DataFrame()
            
        if conv_MAP_PMU==True:
            dState_MAP_PMU[ts].append(get_state(graph,n,df_ref=dState_ref[ts]))
            dStateFACTS_MAP_PMU[ts].append(get_state_FACTS(ramTCSC,busSVC,ramUPFC,n,df_ref=dStateFACTS_ref[ts]))

        
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
dfconv.to_csv("ResultadosISGT/"+file+"resultados_conv_"+sys+str(cx)+Meas+nome+".csv")
#%%
dfSATES["error"]=np.abs(dfSATES["val"]-dfSATES["val_ref"])

dfSATES.to_csv("ResultadosISGT/"+file+"state_"+sys+str(cx)+Meas+nome+".csv")

dfSATES_FACTS["error"]=np.abs(dfSATES_FACTS["val"]-dfSATES_FACTS["val_ref"])
dfSATES_FACTS.to_csv("ResultadosISGT/"+file+"state_FACTS_"+sys+str(cx)+Meas+nome+".csv")
#%%