import pandas as pd
import numpy as np
from networkcalc import *


def create_dfmeasTCSC(dfDMEASpf,lstTCSC):
    """
    function to filter the TCSC measurements in the dfDMEASpf given the branches in the
    lstFP. It recives the dfDMEASpf data frame with all the possible measurements avaible in the network
    obatined by the load flow and returns only the ones desired.
    @param: dfDMEASpf: pandas dataframe with all the measurements avaible in the loadflow
    @param: lstFP: list with the branches with that type of measurement
    @return: dfFLOW: pandas dataframe with the measurements filterd
    """
    dfTCSC=pd.DataFrame()

    if len(lstTCSC)<1:
        return dfDMEASpf[dfDMEASpf['type']==-1]
    for item in lstTCSC:
        [fr,to]=item.split("-")
        dfTCSC=pd.concat([dfTCSC,dfDMEASpf[((dfDMEASpf["type"]==10)) &(dfDMEASpf["from"]==int(fr)) & (dfDMEASpf["to"]==int(to))]])
    return dfTCSC



def create_dfmeasUPFCVsh(dfDMEASpf,lstUPFC):
    """
    function to filter the UPFC Vsh measurements in the dfDMEASpf given the branches in the
    lstFP. It recives the dfDMEASpf data frame with all the possible measurements avaible in the network
    obatined by the load flow and returns only the ones desired.
    @param: dfDMEASpf: pandas dataframe with all the measurements avaible in the loadflow
    @param: lstUPFC: list with the branches with that type of measurement
    @return: dfmeasUPFCVsh: pandas dataframe with the measurements filterd
    """
    dfmeasUPFCVsh=pd.DataFrame()

    if len(lstUPFC)<1:
        return dfDMEASpf[dfDMEASpf['type']==-1]
    for item in lstUPFC:
        [fr,to]=item.split("-")
        dfmeasUPFCVsh=pd.concat([dfmeasUPFCVsh,dfDMEASpf[((dfDMEASpf["type"]==12)) &(dfDMEASpf["from"]==int(fr)) & (dfDMEASpf["to"]==int(to))]])
    return dfmeasUPFCVsh



def create_dfmeasUPFCtsh(dfDMEASpf,lstUPFC):
    """
    function to filter the UPFC tsh measurements in the dfDMEASpf given the branches in the
    lstFP. It recives the dfDMEASpf data frame with all the possible measurements avaible in the network
    obatined by the load flow and returns only the ones desired.
    @param: dfDMEASpf: pandas dataframe with all the measurements avaible in the loadflow
    @param: lstUPFC: list with the branches with that type of measurement
    @return: dfmeasUPFCtsh: pandas dataframe with the measurements filterd
    """
    dfmeasUPFCtsh=pd.DataFrame()

    if len(lstUPFC)<1:
        return dfDMEASpf[dfDMEASpf['type']==-1]
    for item in lstUPFC:
        [fr,to]=item.split("-")
        dfmeasUPFCtsh=pd.concat([dfmeasUPFCtsh,dfDMEASpf[((dfDMEASpf["type"]==13)) &(dfDMEASpf["from"]==int(fr)) & (dfDMEASpf["to"]==int(to))]])
    return dfmeasUPFCtsh

def create_dfmeasUPFCVse(dfDMEASpf,lstUPFC):
    """
    function to filter the UPFC Vse measurements in the dfDMEASpf given the branches in the
    lstFP. It recives the dfDMEASpf data frame with all the possible measurements avaible in the network
    obatined by the load flow and returns only the ones desired.
    @param: dfDMEASpf: pandas dataframe with all the measurements avaible in the loadflow
    @param: lstUPFC: list with the branches with that type of measurement
    @return: dfmeasUPFCVse: pandas dataframe with the measurements filterd
    """
    dfmeasUPFCVse=pd.DataFrame()

    if len(lstUPFC)<1:
        return dfDMEASpf[dfDMEASpf['type']==-1]
    for item in lstUPFC:
        [fr,to]=item.split("-")
        dfmeasUPFCVse=pd.concat([dfmeasUPFCVse,dfDMEASpf[((dfDMEASpf["type"]==14)) &(dfDMEASpf["from"]==int(fr)) & (dfDMEASpf["to"]==int(to))]])
    return dfmeasUPFCVse

def create_dfmeasUPFCtse(dfDMEASpf,lstUPFC):
    """
    function to filter the UPFC tse measurements in the dfDMEASpf given the branches in the
    lstFP. It recives the dfDMEASpf data frame with all the possible measurements avaible in the network
    obatined by the load flow and returns only the ones desired.
    @param: dfDMEASpf: pandas dataframe with all the measurements avaible in the loadflow
    @param: lstUPFC: list with the branches with that type of measurement
    @return: create_dfmeasUPFCtse: pandas dataframe with the measurements filterd
    """
    dfmeasUPFCVse=pd.DataFrame()

    if len(lstUPFC)<1:
        return dfDMEASpf[dfDMEASpf['type']==-1]
    for item in lstUPFC:
        [fr,to]=item.split("-")
        dfmeasUPFCVse=pd.concat([dfmeasUPFCVse,dfDMEASpf[((dfDMEASpf["type"]==15)) &(dfDMEASpf["from"]==int(fr)) & (dfDMEASpf["to"]==int(to))]])
    return dfmeasUPFCVse



def create_dfmeasSVC(dfDMEASpf,lst_svc):
    """
    Funcion to filter the SVC variable measurements in the the dfDMEASpf given buses in the
    list lst_IP. It recives the dfDMEASpf data frame with all the possible measurements avaible in the network
    obatined by the load flow  and returns only the ones desired.
    @param: dfDMEASpf: pandas dataframe with all the measurements avaible in the loadflow
    @param: lst_svc: list with the buses with that type of measurement
    """
    if len(lst_svc)<1:
        return dfDMEASpf[dfDMEASpf['type']==-1]
    return dfDMEASpf[((dfDMEASpf["type"]==11)) & (dfDMEASpf["from"].isin(lst_svc))]



def create_dfFluxo(dfDMEASpf,lstFP):
    """
    function to filter the flow measurements in the dfDMEASpf given the branches in the
    lstFP. It recives the dfDMEASpf data frame with all the possible measurements avaible in the network
    obatined by the load flow and returns only the ones desired.
    @param: dfDMEASpf: pandas dataframe with all the measurements avaible in the loadflow
    @param: lstFP: list with the branches with that type of measurement
    @return: dfFLOW: pandas dataframe with the measurements filterd
    """
    dfFLOW=pd.DataFrame()

    if len(lstFP)<1:
        return dfDMEASpf[dfDMEASpf['type']==-1]
    for item in lstFP:
        [fr,to]=item.split("-")
        dfFLOW=pd.concat([dfFLOW,dfDMEASpf[((dfDMEASpf["type"]==2) |(dfDMEASpf["type"]==3)) &(dfDMEASpf["from"]==int(fr)) & (dfDMEASpf["to"]==int(to))]])
    return dfFLOW

def create_dfFluxo_PMU(dfDMEASpf,lstFP):
    """
    function to filter the current flow measurements in the dfDMEASpf given the branches in the
    lstFP. It recives the dfDMEASpf data frame with all the possible measurements avaible in the network
    obatined by the load flow and returns only the ones desired.
    @param: dfDMEASpf: pandas dataframe with all the measurements avaible in the loadflow
    @param: lstFP: list with the branches with that type of measurement
    @return: dfFLOW: pandas dataframe with the measurements filterd
    """
    dfFLOW=pd.DataFrame()

    if len(lstFP)<1:
        return dfDMEASpf[dfDMEASpf['type']==-1]
    for item in lstFP:
        [fr,to]=item.split("-")
        dfFLOW=pd.concat([dfFLOW,dfDMEASpf[((dfDMEASpf["type"]==8) |(dfDMEASpf["type"]==9)) &(dfDMEASpf["from"]==int(fr)) & (dfDMEASpf["to"]==int(to))]])
    return dfFLOW

def create_dfIP(dfDMEASpf,lst_IP):
    """
    Funcion to filter the power injection measurements in the the dfDMEASpf given buses in the
    list lst_IP. It recives the dfDMEASpf data frame with all the possible measurements avaible in the network
    obatined by the load flow  and returns only the ones desired.
    @param: dfDMEASpf: pandas dataframe with all the measurements avaible in the loadflow
    @param: lst_IP: list with the buses with that type of measurement
    """
    if len(lst_IP)<1:
        return dfDMEASpf[dfDMEASpf['type']==-1]
    return dfDMEASpf[((dfDMEASpf["type"]==0)|(dfDMEASpf["type"]==1)) & (dfDMEASpf["from"].isin(lst_IP))]


def create_dfIC_PMUs(dfDMEASpf,lst_IP):
    """
    Funcion to filter the current PMUs injection measurements in the the dfDMEASpf given buses in the
    list lst_IP. It recives the dfDMEASpf data frame with all the possible measurements avaible in the network
    obatined by the load flow  and returns only the ones desired.
    @param: dfDMEASpf: pandas dataframe with all the measurements avaible in the loadflow
    @param: lst_IP: list with the buses with that type of measurement
    """
    if len(lst_IP)<1:
        return dfDMEASpf[dfDMEASpf['type']==-1]
    return dfDMEASpf[((dfDMEASpf["type"]==6)|(dfDMEASpf["type"]==7)) & (dfDMEASpf["from"].isin(lst_IP))]


def create_dfV(dfDMEASpf,lst_V):
    """
    Funcion to filter the voltage magnitude measurements in the the dfDMEASpf given buses in the
    list lst_V. It recives the dfDMEASpf data frame with all the possible measurements avaible in the network
    obatined by the load flow  and returns only the ones desired.
    @param: dfDMEASpf: pandas dataframe with all the measurements avaible in the loadflow
    @param: lst_V: list with the buses with that type of measurement
    """
    return dfDMEASpf[(dfDMEASpf["type"]==4)& (dfDMEASpf["from"].isin(lst_V))]

def create_dfV_PMUs(dfDMEASpf,lst_V):
    """
    Funcion to filter the voltage magnitude measurements in the the dfDMEASpf given buses in the
    list lst_V. It recives the dfDMEASpf data frame with all the possible measurements avaible in the network
    obatined by the load flow  and returns only the ones desired.
    @param: dfDMEASpf: pandas dataframe with all the measurements avaible in the loadflow
    @param: lst_V: list with the buses with that type of measurement
    """
    return dfDMEASpf[((dfDMEASpf["type"]==4)|(dfDMEASpf["type"]==5))& (dfDMEASpf["from"].isin(lst_V))]



def create_DMEAS(sys,prec,graph,bran,dUPFC={},dfDMEASpf=pd.DataFrame()):
    """
    Creates a DMEAS file with the measurements according to the "measplan.csv" file
    if, it reads the measurements avaible in the "DMEAS_pf.csv" file, if it do not exits it runs
    the load flow and creates it. The function recives @sys a string with the name of the system's file
    and the prec dictionary with the pr parameter for each measurement
    @param: sys-string with the name of the system's file
    @param: prec - dictionary with the precision of each measurement type
    @return: dfDMEAS - pandas dictionary with the measurement set   
    """
    #read the file with the measurement pla
    if dfDMEASpf.empty:

        try: # if the DMEAS exists the program reads it, this file is not mandatory for power flow 
            dfDMEASpf=pd.read_csv(sys+"/DMEAS_pf.csv",header=None)
            dfDMEASpf.columns=["type","from","to","zmeas","prec"]
        except:
            conv = load_flow(graph,tol=1e-10)
            save_DMEAS_pf(graph,bran,sys,dUPFC)
            dfDMEASpf=pd.read_csv(sys+"/DMEAS_pf.csv",header=None)
            dfDMEASpf.columns=["type","from","to","zmeas","prec"]

    try:
        df=pd.read_csv(sys+"/measplan.csv",keep_default_na=False)
    except:
        print("There is no measurement plan file")
        exit()
    
    prec_standard={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.01,"SMP":0.01,"SMP":0.01,"SMV":0.01,"PSEUDO":0.01,"VIRTUAL":0.01,"PMU_If":0.001,"PMU_Iinj":0.001,"PMUs_V":0.001}
    


    for key in list(set(prec_standard.keys())-(prec.keys())):
        prec[key]=prec_standard[key]

    SCADAlstIP=list(np.int32(list(filter(None,df["PISCADA"].to_list()))))
    SCADAlstFP=list(filter(None,df["PFSCADA"].to_list()))
    SCADAlstV=list(np.int32(list(filter(None,df["VSCADA"].to_list()))))
    PMUslst_If=list(filter(None,df["PMU_If"].to_list()))
    PMUslst_Iinj=list(np.int32(list(filter(None,df["PMU_Iinj"].to_list()))))
    PMUslst_V=list(np.int32(list(filter(None,df["PMU_V"].to_list()))))
    SMlstIP=list(np.int32(list(filter(None,df["PISM"].to_list()))))
    SMlstFP=list(filter(None,df["PFSM"].to_list()))
    SMlstV=list(np.int32(list(filter(None,df["VSM"].to_list()))))
    PSEUDOlst=list(np.int32(list(filter(None,df["PSEUDO"].to_list()))))
    Plst=dfDMEASpf[((dfDMEASpf["prec"]<0.0001) &(dfDMEASpf["zmeas"]==0.000) & (dfDMEASpf["type"]==0))]["from"].tolist()
    Qlst=dfDMEASpf[((dfDMEASpf["prec"]<0.0001) &(dfDMEASpf["zmeas"]==0.000) & (dfDMEASpf["type"]==1))]["from"].tolist()
    Vistuaislst=list(set(Plst).intersection(Qlst))
    Vistuaislst=list(set(Vistuaislst)-set(Vistuaislst).intersection(SCADAlstIP+SMlstIP+PSEUDOlst))

    dfPISCADA=create_dfIP(dfDMEASpf,SCADAlstIP)

    dfPFSCADA=create_dfFluxo(dfDMEASpf,SCADAlstFP)

    dfVSCADA=create_dfV(dfDMEASpf,SCADAlstV)

    dfIfPMU=create_dfFluxo_PMU(dfDMEASpf,PMUslst_If)
    dfIinjPMU=create_dfIC_PMUs(dfDMEASpf,PMUslst_Iinj)
    dfVPMU=create_dfV_PMUs(dfDMEASpf,PMUslst_V)

    dfIPSM=create_dfIP(dfDMEASpf,SMlstIP)

    dfFPSM=create_dfFluxo(dfDMEASpf,SMlstFP)

    dfVSM=create_dfV(dfDMEASpf,SMlstV)

    dfPSEUDO=create_dfIP(dfDMEASpf,PSEUDOlst)

    dfVirtuais=create_dfIP(dfDMEASpf,Vistuaislst)
    dfPFSCADA.loc[:,"prec"]=prec["SCADAPF"]
    dfPISCADA.loc[:,"prec"]=prec["SCADAPI"]
    dfVSCADA.loc[:,"prec"]=prec["SCADAV"]


    dfIfPMU.loc[:,"prec"]=prec["PMU_If"]
    dfIinjPMU.loc[:,"prec"]=prec["PMU_Iinj"]
    dfVPMU.loc[:,"prec"]=prec["PMUs_V"]

    dfIPSM.loc[:,"prec"]=prec["SMP"]
    dfFPSM.loc[:,"prec"]=prec["SMP"]
    dfVSM.loc[:,"prec"]=prec["SMV"]
    dfPSEUDO.loc[:,"prec"]=prec["PSEUDO"]
    dfVirtuais.loc[:,"prec"]=prec["VIRTUAL"]

    dfDMEAS=pd.concat([dfPISCADA,dfIPSM,dfPSEUDO,dfVirtuais,dfPFSCADA,dfFPSM,dfVSCADA,dfVSM,dfIfPMU,dfIinjPMU,dfVPMU])
    return dfDMEAS

def insert_res(dfDMEASsr):
    """
    Inserts gaussian noise in the measurement set, with variance according with the 
    precision and the magnitude of the measurement.
    """

    e=np.random.normal(size=(len(dfDMEASsr)))
    for i in range(len(e)):
        if e[i]>2.5:
            e[i]=2.5
        elif e[i]<-2.5:
            e[i]=-2.5
    dfDMEASr=dfDMEASsr.copy()
    dfDMEASr.loc[:,"zmeas"]=dfDMEASsr["zmeas"]+e*dfDMEASsr["prec"]*np.abs(dfDMEASsr["zmeas"])/3
    return dfDMEASr

def insert_EG(dfDMEASsr,dfEG,duplicate=False):
    """
    Inserts Gross Error in measruements in the measurement set, the measurements are selected following the LST file.

    """
    
    for idx,meas in dfEG.iterrows():
        tipo=meas["type"]
        fr=meas["from"]
        to=meas["to"]
        mag=meas["magnitude"]
        mul=meas["multi"]

        if tipo in [0,1,4,11]:
            mask=(dfDMEASsr["type"]==tipo) & (dfDMEASsr["from"]==fr)
        else: 
            mask=(dfDMEASsr["type"]==tipo) & (dfDMEASsr["from"]==fr) & (dfDMEASsr["to"]==to)
        if mul == 0:
            for idx2, row in dfDMEASsr[mask].iterrows():
                    sigma=row["prec"]*np.abs(row["zmeas"])/3
                    dfDMEASsr.at[idx2,"zmeas"]=-row["zmeas"]
                    # +mag*sigma

                    break
        else:
            i=0
            for idx2, row in dfDMEASsr[mask].iterrows():
                sigma=row["prec"]*np.abs(row["zmeas"])/3
                dfDMEASsr.at[idx2,"zmeas"]=row["zmeas"]+mag*sigma
                if i == mul:
                    break
                i=i+1

    

    

    return dfDMEASsr



def create_DMEAS_FACTS(sys,prec,graph,bran,branUPFC,dfDMEASpf=pd.DataFrame()):
    """
    Creates a DMEAS part for the FACTS with the measurements according to the "measplan_FACTS.csv" file
    if, it reads the measurements avaible in the "DMEAS_pf.csv" file, if it do not exits it runs
    the load flow and creates it. The function recives @sys a string with the name of the system's file
    and the prec dictionary with the pr parameter for each measurement
    @param: sys-string with the name of the system's file
    @param: prec - dictionary with the precision of each measurement type
    @return: dfDMEAS - pandas dictionary with the measurement set   
    """
    #read the file with the measurement plan
    if dfDMEASpf.empty:
        try: # if the DMEAS exists the program reads it, this file is not mandatory for power flow 
            dfDMEASpf=pd.read_csv(sys+"/DMEAS_pf.csv",header=None)
            dfDMEASpf.columns=["type","from","to","zmeas","prec"]
        except:
            conv = power_flow(graph,tol=1e-10)
            save_DMEAS_pf(graph,bran,sys,branUPFC)
            dfDMEASpf=pd.read_csv(sys+"/DMEAS_pf.csv",header=None)
            dfDMEASpf.columns=["type","from","to","zmeas","prec"]
    try:
        df=pd.read_csv(sys+"/measplanFACTS.csv",keep_default_na=False)
    except:
        print("There is no measurement fatcs plan file")
        quit()


    
    prec_standard={"TCSCvar":0.01,"SVCvar":0.01,"UPFCt_sh":0.01,"UPFCV_sh":0.01,"UPFCt_se":0.01,"UPFCV_se":0.01}
    
    for key in list(set(prec_standard.keys())-(prec.keys())):
        prec[key]=prec_standard[key]


    TCSCvar=list(filter(None,df["TCSCvar"].to_list()))
    SVCvar=list(np.int32(list(filter(None,df["SVCvar"].to_list()))))
    UPFCt_se=list(filter(None,df["UPFCt_se"].to_list()))
    UPFCV_se=list(filter(None,df["UPFCV_se"].to_list()))
    UPFCt_sh=list(filter(None,df["UPFCt_sh"].to_list()))
    UPFCV_sh=list(filter(None,df["UPFCV_sh"].to_list()))


    dfmeasTCSC=create_dfmeasTCSC(dfDMEASpf,TCSCvar)

    dfmeasSVCvar=create_dfmeasSVC(dfDMEASpf,SVCvar)

    dfcreate_dfmeasUPFCVsh=create_dfmeasUPFCVsh(dfDMEASpf,UPFCV_sh)
    dfcreate_dfmeasUPFCtsh=create_dfmeasUPFCtsh(dfDMEASpf,UPFCt_sh)
    dfcreate_dfmeasUPFCVse=create_dfmeasUPFCVse(dfDMEASpf,UPFCV_se)
    dfcreate_dfmeasUPFCtse=create_dfmeasUPFCtse(dfDMEASpf,UPFCt_se)


    dfmeasTCSC.loc[:,"prec"]=prec["TCSCvar"]
    dfmeasSVCvar.loc[:,"prec"]=prec["SVCvar"]
    dfcreate_dfmeasUPFCVsh.loc[:,"prec"]=prec["UPFCt_sh"]
    dfcreate_dfmeasUPFCtsh.loc[:,"prec"]=prec["UPFCV_sh"]
    dfcreate_dfmeasUPFCVse.loc[:,"prec"]=prec["UPFCt_se"]
    dfcreate_dfmeasUPFCtse.loc[:,"prec"]=prec["UPFCV_se"]
 

    dfDMEAS=pd.concat([dfmeasTCSC,dfmeasSVCvar,dfcreate_dfmeasUPFCVsh,dfcreate_dfmeasUPFCtsh,dfcreate_dfmeasUPFCVse,dfcreate_dfmeasUPFCtse])
    return dfDMEAS