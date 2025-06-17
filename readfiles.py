from classes import *
import pandas as pd
import numpy as np

def read_files_old(sys):
    """
    This function performs the reading of the files with the information about the Power System.
    @param: sys - string with the name of the system
    @return dfDBUS - Data Frame with the information about the system's buses
    @return dfDBRAN - Data Frame with the information about the system's branches
    @return dfDMEAS - Data Frame with the information about the system measurements
    @return dfDFACTS - Data Frame with the FACTS devices
    """
    try: # if the DBUS exists the program reads it, if not it stops. This file is mandatory 
        dfDBUS=pd.read_csv(sys+"/DBUS.csv",header=None,dtype={0:np.int64,1:np.int64})
        dfDBUS.columns=["id","type","V","theta","Pg","Qg","Pd","Qd","Bs"]
    except:
        print("Error while reading DBUS file")
        quit()

    try: # if the DBRAN exists the program reads it, if not it stops. This file is mandatory
        dfDBRAN=pd.read_csv(sys+"/DBRAN.csv",header=None,dtype={0:np.int64,1:np.int64,2:np.int64,3:np.int64})
        dfDBRAN.columns=["id","type","from","to","r","x","bsh","tap"]
    except:
        print("Error while reading DBRAN file")
        exit(1)
    try: # if the DMEAS exists the program reads it, this file is not mandatory for power flow 
        dfDMEAS=pd.read_csv(sys+"/DMEAS.csv",header=None)
        dfDMEAS.columns=["type","from","to","zmeas","prec"]
    except:
        print("There is no DMEAS")
        dfDMEAS=[]
    try: # if the DMEAS exists the program reads it, this file is not mandatory for power flow 
        dfDTCSC=pd.read_csv(sys+"/DTCSC.csv",header=None,dtype={0:np.int64,1:np.int64,2:np.int64,3:np.float64,4:np.float64,5:np.float64})
        dfDTCSC.columns=["id","from","to","a","xtscc_ini","Pfesp"]
        dfDTCSC["type"]=0
    except:
        print("There is no DTCSC")
        dfDTCSC=pd.DataFrame()   
    try: # if the DMEAS exists the program reads it, this file is not mandatory for power flow 
        dfDSVC=pd.read_csv(sys+"/DSVC.csv",header=None,dtype={0:np.int64,1:np.int64,2:np.float64,3:np.float64,4:np.float64,5:np.float64,6:np.float64,7:np.float64,8:np.float64,9:np.float64})
        dfDSVC.columns=["id","bus","Rt","Xt","Bini","Bmax","Bmin","aini","amax","amin"]
        dfDSVC["type"]=1
    except:
        print("There is no DSVC")
        dfDSVC=pd.DataFrame()   
    try: # if the DMEAS exists the program reads it, this file is not mandatory for power flow 
        dfUPFC=pd.read_csv(sys+"/DUPFC.csv",header=None,dtype={0:np.int64,1:np.int64,2:np.float64,3:np.float64,4:np.float64,5:np.float64,6:np.float64,7:np.float64,8:np.float64,9:np.float64})
        dfUPFC.columns=["id","from","to","Vse","t_se","Vsh","t_sh","Psp","Qsp","Vp","Rse","Xse","Rsh","Xsh","Vse_max","Vse_min","Vsh_max","Vsh_min","mode"]
        dfUPFC["type"]=2
    except:
        print("There is no DUPFC")
        dfUPFC=pd.DataFrame()   
    try:
        dfDFACTS=pd.concat([dfDTCSC,dfDSVC,dfUPFC], axis=0, ignore_index=True)
    except:
        dfDFACTS=pd.DataFrame()  
    return dfDBUS,dfDBRAN,dfDMEAS,dfDFACTS

def read_files(sys):
    """
    This function performs the reading of the files with the information about the Power System.
    @param: sys - string with the name of the system
    @return DBUS - Data Frame with the information about the system's buses
    @return dfDBRAN - Data Frame with the information about the system's branches
    @return dfDMEAS - Data Frame with the information about the system measurements
    @return dfDFACTS - Data Frame with the FACTS devices
    """
    try: # if the DBUS exists the program reads it, if not it stops. This file is mandatory 
        dfDBUS=pd.read_csv(sys+"/DBUS.csv",header=0,dtype={0:np.int64,1:np.int64})
    except:
        print("Error while reading DBUS file")
        quit()

    try: # if the DBRAN exists the program reads it, if not it stops. This file is mandatory
        dfDBRAN=pd.read_csv(sys+"/DBRAN.csv",header=0,dtype={0:np.int64,1:np.int64,2:np.int64,3:np.int64})
    except:
        print("Error while reading DBRAN file")
        exit(1)
    try: # if the DMEAS exists the program reads it, this file is not mandatory for power flow 
        dfDMEAS=pd.read_csv(sys+"/DMEAS.csv",header=0)
    except:
        print("There is no DMEAS")
        dfDMEAS=[]
    try: # if the DMEAS exists the program reads it, this file is not mandatory for power flow 
        dfDTCSC=pd.read_csv(sys+"/DTCSC.csv",header=None,dtype={0:np.int64,1:np.int64,2:np.int64,3:np.float64,4:np.float64,5:np.float64})
        dfDTCSC.columns=["id","from","to","a","xtscc_ini","Pfesp"]
        dfDTCSC["type"]=0
    except:
        print("There is no DTCSC")
        dfDTCSC=pd.DataFrame()   
    try: # if the DMEAS exists the program reads it, this file is not mandatory for power flow 
        dfDSVC=pd.read_csv(sys+"/DSVC.csv",header=None,dtype={0:np.int64,1:np.int64,2:np.float64,3:np.float64,4:np.float64,5:np.float64,6:np.float64,7:np.float64,8:np.float64,9:np.float64})
        dfDSVC.columns=["id","de","Rt","Xt","Bini","Bmax","Bmin","aini","amax","amin"]
        dfDSVC["type"]=1
    except:
        print("There is no DSVC")
        dfDSVC=pd.DataFrame()   
    try: # if the DMEAS exists the program reads it, this file is not mandatory for power flow 
        dfUPFC=pd.read_csv(sys+"/DUPFC.csv",header=None,dtype={0:np.int64,1:np.int64,2:np.float64,3:np.float64,4:np.float64,5:np.float64,6:np.float64,7:np.float64,8:np.float64,9:np.float64})
        dfUPFC.columns=["id","from","to","Vse","t_se","Vsh","t_sh","Psp","Qsp","Vp","Rse","Xse","Rsh","Xsh","Vse_max","Vse_min","Vsh_max","Vsh_min","mode"]
        dfUPFC["type"]=2
    except:
        print("There is no DUPFC")
        dfUPFC=pd.DataFrame()   
    try:
        dfDFACTS=pd.concat([dfDTCSC,dfDSVC,dfUPFC], axis=0, ignore_index=True)
    except:
        dfDFACTS=pd.DataFrame()  
    return dfDBUS,dfDBRAN,dfDMEAS,dfDFACTS




def read_files_DC(sys):
    """
    This function performs the reading of the files with the information about the Power System.
    @param: sys - string with the name of the system
    @return DBUS_DC - Data Frame with the information about the system's DC buses
    @return dfDBRAN - Data Frame with the information about the system's branches
    @return dfDMEAS - Data Frame with the information about the system measurements
    @return dfDFACTS - Data Frame with the FACTS devices
    """
    try: # if the DBUS exists the program reads it, if not it stops. This file is mandatory 
        dfDBUS_DC=pd.read_csv(sys+"/DBUS_DC.csv",header=0,dtype={0:np.int64,1:np.int64})
    except:
        print("Error while reading DBUS DBUS_DC file")
        quit()

    try: # if the DBRAN exists the program reads it, if not it stops. This file is mandatory
        dfDBRAN_DC=pd.read_csv(sys+"/DBRAN_DC.csv",header=0,dtype={0:np.int64,1:np.int64,2:np.int64})
    except:
        print("Error while reading DBRAN_DC file")
        exit(1)

    try:
        dfDCONV_acdc=pd.read_csv(sys+"/DCONV_ACDC.csv",header=0,dtype={0:np.int64,1:np.int64})
    except: 
        print("There is no DCONV_acdc")
        dfDCONV_acdc=pd.DataFrame()

    return dfDBUS_DC,dfDBRAN_DC,dfDCONV_acdc


def prt_state(graph):
    """
    Function to print in the scream the value of the state variables, in the network's graph
    @param: graph Graph structure with the information about the network
    """
    for no in graph:
        s="Bus: {:d} | V : {:f} | t : {:f}".format(no.bus.id,no.V,no.theta*180/np.pi)
        print(s)

def prt_state_dc(graph_dc):
    """
    Function to print in the scream the value of the state variables, in the network's graph
    @param: graph Graph structure with the information about the network
    """
    for no in graph_dc:
        s="Bus: {:d} | V : {:f}".format(no.bus_dc.id,no.Vdc)
        print(s)


def prt_state_FACTS(graph,var_x,var_svc,var_upfc):
    """
    Function to print in the scream the value of the state variables, in the network's graph
    @param: graph Graph structure with the information about the network
    """
    for key,item in var_x.items():
        k=int(key.split("-")[0])
        m=int(key.split("-")[1])
        s="TCSC | from {:d} | to {:d}| X : {:f}".format(graph[k].bus.id,graph[m].bus.id,graph[k].adjk[key].xtcsc)
        print(s)
    for key,item in var_svc.items():
        k=int(key)
        s="SVC | Bus {:d} | B_SVC : {:f}".format(graph[k].bus.id,graph[k].SVC.BSVC)
        print(s)
    
    for key, item in var_upfc.items():
        k=int(key.split("-")[0])
        m=int(key.split("-")[1])


        s="UPFC | from {:d} | to {:d}| Vse: {:f} | Tse {:f} |  Vsh: {:f} | Tsh {:f}"\
            .format(graph[k].bus.id,graph[m].bus.id,graph[k].bUFPC_adjk[key].Vse,\
                    graph[k].bUFPC_adjk[key].t_se*180/np.pi,graph[k].bUFPC_adjk[key].Vsh,graph[k].bUFPC_adjk[key].t_sh*180/np.pi)
        print(s)


def save_DMEAS_pf(graph,bran,sys,dUPFC={}):
    """
    Function to save the file with all measurements possible, from a load flow simulation. 
    It use the graph of the network to calculate every possible measurement and save it in a file called 
    DMEAS_fp.csv into the system's folder.
    @param: graph Graph structure with the information about the network
    @param: ram dictionary with the information about the network branches
    @sys: string with the system folder's name
    """
    meas=[] 
    Pinj=[]
    Qinj=[]
    Vmod=[]
    Vangl=[]
    Pkm=[]
    Pmk=[]
    Qkm=[]
    Qmk=[]
    Ikm_re=[]
    Imk_re=[]
    Ikm_im=[]
    Imk_im=[]
    Iinj_re=[]
    Iinj_im=[]
    
    #calculates the Power Inejection (Reactive and Active)
    for no in graph:
        linha=[0,no.bus.id,-1,no.P(graph),1]
        Pinj.append(linha)
        linha=[1,no.bus.id,-1,no.Q(graph),1]
        Qinj.append(linha)
        linha=[4,no.bus.id,-1,no.V,1]
        Vmod.append(linha)
        linha=[5,no.bus.id,-1,no.theta,1]
        Vangl.append(linha)

    #calculates the flows in the branches
    for key,r in bran.items():
        #calculate from k to m
        linha=[2,graph[r.fr].bus.id,graph[r.to].bus.id,r.Pf(graph,0),1.0]
        linha2=[3,graph[r.fr].bus.id,graph[r.to].bus.id,r.Qf(graph,0),1.0]
        Pkm.append(linha)
        Qkm.append(linha2)
        #calculate from m to k
        linha=[2,graph[r.to].bus.id,graph[r.fr].bus.id,r.Pf(graph,1),1.0]
        linha2=[3,graph[r.to].bus.id,graph[r.fr].bus.id,r.Qf(graph,1),1.0]
        Pmk.append(linha)
        Qmk.append(linha2)


 
    #calculates the flows in the upfc
    for key,upfc in dUPFC.items():
        linha=[2,graph[upfc.p].bus.id,graph[upfc.s].bus.id,upfc.Pps(graph),1.0]
        linha2=[3,graph[upfc.p].bus.id,graph[upfc.s].bus.id,upfc.Qps(graph),1.0]
        Pkm.append(linha)
        Qkm.append(linha2)
        #calculate from m to k
        linha=[2,graph[upfc.s].bus.id,graph[upfc.p].bus.id,upfc.Psp(graph),1.0]
        linha2=[3,graph[upfc.s].bus.id,graph[upfc.p].bus.id,upfc.Qsp(graph),1.0]
        Pmk.append(linha)
        Qmk.append(linha2)




    for no in graph:
        linha=[6,no.bus.id,-1,no.I_inj_re(graph),1]
        Iinj_re.append(linha)
        linha=[7,no.bus.id,-1,no.I_inj_im(graph),1]
        Iinj_im.append(linha)


     #calculates the current in the branches
    for key,r in bran.items():
        #calculate from k to m
        linha=[8,graph[r.fr].bus.id,graph[r.to].bus.id,r.Iref(graph,0),1.0]
        linha2=[9,graph[r.fr].bus.id,graph[r.to].bus.id,r.Iimf(graph,0),1.0]
        Ikm_re.append(linha)
        Ikm_im.append(linha2)
        #calculate from m to k
        linha=[8,graph[r.to].bus.id,graph[r.fr].bus.id,r.Iref(graph,1),1.0]
        linha2=[9,graph[r.to].bus.id,graph[r.fr].bus.id,r.Iimf(graph,1),1.0]
        Imk_re.append(linha)
        Imk_im.append(linha2)


    for key,upfc in dUPFC.items():
        linha=[8,graph[upfc.p].bus.id,graph[upfc.s].bus.id,upfc.Ips_re(graph),1.0]
        linha2=[9,graph[upfc.p].bus.id,graph[upfc.s].bus.id,upfc.Ips_im(graph),1.0]
        Ikm_re.append(linha)
        Ikm_im.append(linha2)
        #calculate from m to k
        linha=[8,graph[upfc.s].bus.id,graph[upfc.p].bus.id,upfc.Isp_re(graph),1.0]
        linha2=[9,graph[upfc.s].bus.id,graph[upfc.p].bus.id,upfc.Isp_im(graph),1.0]
        Imk_re.append(linha)
        Imk_im.append(linha2)

    Xtcsc=[]
    BSVC=[]
    Vsh=[]
    t_sh=[]
    Vse=[]
    t_se=[]
    for no in graph:
        if no.FlagTCSC==True:
            for key,item in  no.bFACTS_adjk.items():
                k=int(key.split("-")[0])
                m=int(key.split("-")[1])
                linha=[10,graph[k].bus.id,graph[m].bus.id,item.xtcsc,1.0]
                Xtcsc.append(linha)
        if no.FlagSVC==True:
            linha=[11,no.bus.id,-1,no.SVC.BSVC,1.0]
            BSVC.append(linha)
        if no.FlagUPFC==True:
            for key,item in  no.bUFPC_adjk.items():
                k=int(key.split("-")[0])
                m=int(key.split("-")[1])
                linha=[12,graph[k].bus.id,graph[m].bus.id,item.Vsh,1.0]
                linha1=[13,graph[k].bus.id,graph[m].bus.id,graph[k].theta-item.t_sh,1.0]
                linha2=[14,graph[k].bus.id,graph[m].bus.id,item.Vse,1.0]
                linha3=[15,graph[k].bus.id,graph[m].bus.id,graph[k].theta-item.t_se,1.0]
                Vsh.append(linha)
                t_sh.append(linha1)
                Vse.append(linha2)
                t_se.append(linha3)










    meas=Pinj+Qinj+Pkm+Qkm+Pmk+Qmk+Vmod+\
    Vangl+Ikm_re+Ikm_im+Imk_re+Imk_im+Iinj_re+Iinj_im\
    +Xtcsc+BSVC+Vsh+t_sh+Vse+t_se


    
    dfDMEAS=pd.DataFrame(meas,columns=["type","from","to","zmeas","prec"])
    dfDMEAS.to_csv(sys+"/DMEAS_fp.csv",index=False,float_format="%.7f",header=True)
    return dfDMEAS



def save_DBUS(graph):

    id=[]
    tipo=[]
    V=[]
    theta=[]
    Pg=[]
    Qg=[]
    Pd=[]
    Qd=[]
    Bs=[]
    for no in graph:
        id.append(no.bus.id)
        tipo.append(no.bus.type)
        V.append(no.V)
        theta.append(no.theta*180/np.pi)
        Pg.append(no.bus.Pg*100)
        Qg.append(no.bus.Qg*100)
        Pd.append(no.bus.Pd*100)
        Qd.append(no.bus.Qd*100)
        Bs.append(no.bus.Bs*100)


    d={"id":id,"tipo":tipo,"V":V,"theta":theta,"Pg":Pg,"Qg":Qg,"Pd":Pd,"Qd":Qd,"Bs":Bs}
    dfDBUS=pd.DataFrame(d)

    dfDBUS.to_csv("DBUS.csv",header=None,index=None,float_format="%.7f")


