#%% Simulações de EGs
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
import copy


#%% Lê arquivos e constroi a estrutura da rede

sys="IEEE14"
measFACTS=False

if measFACTS==True: #nomeclatura dos arquivos de entrada
    Meas="ComMedidas"
else:
    Meas="SemMedidas"

dfEG=pd.read_csv(sys+"/DEG.csv",header=None)
dfEG.columns=["type","de","para","magnitude","multi"]


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


conv=load_flow_FACTS(graph,inici=1,prt=1,itmax=20,printgrad=0,printres=0)

# #%%
#     #get states and 
if conv==1:    
    dDMEDfps=save_DMED_fp(graph,ram,sys,ramUPFC)
    dState_ref=get_state(graph)
    

# #%%
dfSATES_ref=pd.DataFrame() #salva os valores de referência das variáveis de estado normais
# dfSATES_FACTS_ref=pd.DataFrame() #salva os valores de referência das variáveis de estado dos FACTS

for key,item in dState_ref.items():
    df=item
    df["method"]="PF"
    df["scenario"]=key
    dfSATES_ref=pd.concat([dfSATES_ref,df])
    
# for key,item in dStateTCSC_ref.items():
#     df=item
#     df["method"]="PF"
#     df["scenario"]=key
#     dfSATES_FACTS_ref=pd.concat([dfSATES_FACTS_ref,df])

dfSATES_ref.to_csv("ResultadosPSCC/state_ref"+sys+"_EGs.csv")
# dfSATES_FACTS_ref.to_csv("ResultadosPSCC/state_FACTS_ref"+sys+"_EGs.csv")
#%%
# #%%
if measFACTS==True:
    dfDMEDs={}
    
    prec={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.01,"SMP":0.05,"SMV":0.03,"PSEUDO":0.3,"VIRTUAL":1e-5,"TCSCvar":0.02,"SVCvar":0.02,"UPFCt_sh":0.02,"UPFCV_sh":0.02,"UPFCt_se":0.02,"UPFCV_se":0.05}
    dfDMED=create_DMED(sys,prec,graph,ram,ramUPFC,dfDMEDfp=dDMEDfps)
    dfDMEDFACTs=create_DMED_FACTS(sys,prec,graph,ram,ramUPFC,dfDMEDfp=dDMEDfps)
    dfDMEDsr=pd.concat([dfDMED.copy(),dfDMEDFACTs.copy()])
    dfDMEDs=dfDMEDsr.copy()
else:
    dfDMEDs={}
    prec={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.01,"SMP":0.05,"SMV":0.03,"PSEUDO":0.3,"VIRTUAL":1e-5,"TCSCvar":0.01,"SVCvar":0.01,"UPFCt_sh":0.01,"UPFCV_sh":0.01,"UPFCt_se":0.01,"UPFCV_se":0.01}
    dfDMED=create_DMED(sys,prec,graph,ram,ramUPFC,dfDMEDfp=dDMEDfps)
    dfDMEDs=dfDMED.copy()


#%%
conv_LMs={}
conv_BCs={}
conv_noBCs={}
nits_LMs={}
nits_BCs={}
nits_noBCs={}
N=1

dState_LM={}
dStateFACTS_LM={}
dState_BC={}
dStateFACTS_BC={}
dState_noBC={}
dStateFACTS_noBC={}
dfITS=pd.DataFrame()
dconv={}
dconv["n"]=[]
dconv["convLM"]=[]
dconv["convGN"]=[]
dconv["convGNbc"]=[]
dconv["nitsLM"]=[]
dconv["nitsGN"]=[]
dconv["nitsGNbc"]=[]
dconv["caso"]=[]



conv_LMs=[]
conv_BCs=[]
conv_noBCs=[]
nits_LMs=[]
nits_BCs=[]
nits_noBCs=[]
dState_LM=[]
dStateFACTS_LM=[]
dState_BC=[]
dStateFACTS_BC=[]
dState_noBC=[]
dStateFACTS_noBC=[]


for n in range(N): 
    dfDMED=insert_res(dfDMEDs,n)
    # dfDMED=insert_EG(dfDMEDs[idx],dfEG,False)
    # dfDMED=dfDMEDs[idx].copy()
    
    try:
        conv_LM,nits_LM,dfITsLM=SS_WLS_FACTS_LM_BC(graph,dfDMED,ind_i,printgrad=0,printres=0,pirntits=1,flatstart=2,tol=1e-5,tol2=1e-4)
        if conv_LM==1:
            cov=calcCovRes_com_FACTS(graph,dfDMED,ind_i)
            np.savetxt("cov"+Meas+"_idx_Original_Cov.csv",cov)
            df_RES=renorm_com_FACTS(graph,dfDMED,ind_i,cov)
            df_RES.to_csv("dres"+Meas+"_idx_Original.csv",index=None)


    except:
        conv_LM=0
        nits_LM=30
        dfITsLM=pd.DataFrame()
    
    if conv_LM==True:
        dState_LM.append(get_state(graph,n))
        dStateFACTS_LM.append(get_state_FACTS(ramTCSC,busSVC,ramUPFC,n))
    
    conv_BC,nits_BC,dfITsGNbc=SS_WLS_FACTS_withBC(graph,dfDMED,ind_i,flatstart=2,tol=1e-5,tol2=1e-4,printgrad=0,printres=0,pirntits=1)
    
    if conv_BC==True:
        dState_BC.append(get_state(graph,n))
        dStateFACTS_BC.append(get_state_FACTS(ramTCSC,busSVC,ramUPFC,n))

    conv_noBC,nits_noBC,dfITsGN=SS_WLS_FACTS_noBC(graph,dfDMED,ind_i,flatstart=2,tol=1e-5,tol2=1e-4,printgrad=0,printres=0,pirntits=1)
    
    if conv_noBC==True:
        dState_noBC.append(get_state(graph,n))
        dStateFACTS_noBC.append(get_state_FACTS(ramTCSC,busSVC,ramUPFC,n))

    
    conv_LMs.append(conv_LM)
    conv_BCs.append(conv_BC)
    conv_noBCs.append(conv_noBC)
    nits_LMs.append(nits_LM)
    nits_BCs.append(nits_BC)
    nits_noBCs.append(nits_noBC)

    dconv["n"].append(n)
    dconv["convLM"].append(conv_LM)
    dconv["convGN"].append(conv_noBC)
    dconv["convGNbc"].append(conv_BC)
    dconv["nitsLM"].append(nits_LM)
    dconv["nitsGN"].append(nits_noBC)
    dconv["nitsGNbc"].append(nits_BC)


    dfITS=pd.concat([dfITS,dfITsLM,dfITsGNbc,dfITsGN])
    
    
#%%



# dfITS.to_csv("taxa_de_convEG"+str(cx)+Meas+".csv")


# #%%
# dfSATES=pd.DataFrame()
# dfSATES_FACTS=pd.DataFrame()





# for key,item in dState_LM.items():
#     if len(item)>0:
#         df=pd.concat(item)
#         df["method"]="LM"
#         df["scenario"]=key
#         dfSATES=pd.concat([dfSATES,df])
        
# for key,item in dStateFACTS_LM.items():
#     if len(item)>0:
#         df=pd.concat(item)
#         df["method"]="LM"
#         df["scenario"]=key
#         dfSATES_FACTS=pd.concat([dfSATES_FACTS,df])

# for key,item in dState_BC.items():
#     if len(item)>0:
#         df=pd.concat(item)
#         df["method"]="GNbc"
#         df["scenario"]=key
#         dfSATES=pd.concat([dfSATES,df])

# for key,item in dStateFACTS_BC.items():
#     if len(item)>0:
#         df=pd.concat(item)
#         df["method"]="GNbc"
#         df["scenario"]=key
#         dfSATES_FACTS=pd.concat([dfSATES_FACTS,df])


# for key,item in dState_noBC.items():
#     if len(item)>0:
#         df=pd.concat(item)
#         df["method"]="GN"
#         df["scenario"]=key
#         dfSATES=pd.concat([dfSATES,df])


# for key,item in dStateFACTS_noBC.items():
#     if len(item)>0:
#         df=pd.concat(item)
#         df["method"]="GN"
#         df["scenario"]=key
#         dfSATES_FACTS=pd.concat([dfSATES_FACTS,df])



# #%%
# dfconv=pd.DataFrame(data=dconv)
# dfconv.to_csv("ResultadosPSCC/resultados_conv_"+sys+str(cx)+Meas+"EG.csv")
# #%%
# dfSATES.to_csv("ResultadosPSCC/state_"+sys+str(cx)+Meas+".csv")
# dfSATES_FACTS.to_csv("ResultadosPSCC/state_FACTS_"+sys+str(cx)+Meas+"EG.csv")


# #%%
