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
        exit()

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


def prt_state(graph,flag_radians=0):
    """
    Function to print in the scream the value of the state variables, in the network's graph
    @param: graph Graph structure with the information about the network
    """
    if flag_radians==0:
        for no in graph:
            s="Bus: {:s} | V : {:f} | t : {:f}".format(str(no.bus.id),no.V,no.theta*180/np.pi)
            print(s)
    else:
        for no in graph:
            s="Bus: {:d} | V : {:f} | t : {:f}".format(no.bus.id,no.V,no.theta)
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


def save_DMEAS_ac_pf(graph,bran,sys,dUPFC={},flag_save_csv=True):
    """
    Function to save the file with all measurements possible, from a power flow simulation 
    for AC networks with FACTS devices. It uses the graph of the network to calculate every 
    possible measurement and saves it in a file called DMEAS_fp.csv into the system's folder.
    @param: graph Graph structure with the information about the network
    @param: bran Dictionary with the information about the network branches
    @param: sys String with the system folder's name
    Note: This function is specifically designed for AC networks with FACTS devices.
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
    if flag_save_csv:
        dfDMEAS.to_csv(sys+"/DMEAS_fp.csv",index=False,float_format="%.7f",header=True)
    return dfDMEAS


def save_DMEAS_dc_pf(graph_dc,bran_dc,sys,flag_save_csv=True):
    """
    Function to save the file with all DC measurements possible, from a DC power flow simulation.
    It uses the graph of the DC network to calculate every possible measurement and saves it in a file called
    DMEAS_fp.csv into the system's folder.
    @param: graph Graph structure with the information about the DC network
    @param: bran Dictionary with the information about the DC network branches
    @param: sys String with the system folder's name
    Note: This function is specifically designed for DC networks.
    """
    meas=[] 
    Pinj_dc=[]
    Iinj_dc=[]
    Vmod_dc=[]

    Pkm_dc=[]
    Pmk_dc=[]
    
    Ikm_dc=[]
    Imk_dc=[]

    
    

    #calculates the Power Inejection (Reactive and Active)
    for no_dc in graph_dc:
        linha=[100,no_dc.bus_dc.id,-1,no_dc.Pdc(graph_dc),1]
        Pinj_dc.append(linha)
        linha=[101,no_dc.bus_dc.id,-1,no_dc.Idc(graph_dc),1]
        Iinj_dc.append(linha)
        linha=[104,no_dc.bus_dc.id,-1,no_dc.Vdc,1]
        Vmod_dc.append(linha)


    # #calculates the flows in the branches
    for key,r in bran_dc.items():
        #calculate from k to m
        linha=[102,graph_dc[r.fr].bus_dc.id,graph_dc[r.to].bus_dc.id,r.Pfdc(graph_dc,0),1.0]
        Pkm_dc.append(linha)
        linha2=[102,graph_dc[r.to].bus_dc.id,graph_dc[r.fr].bus_dc.id,r.Pfdc(graph_dc,1),1.0]
        Pmk_dc.append(linha2)
        #calculate from m to k
        linha=[103,graph_dc[r.fr].bus_dc.id,graph_dc[r.to].bus_dc.id,r.Ifdc(graph_dc,0),1.0]
        Ikm_dc.append(linha)
        linha2=[103,graph_dc[r.to].bus_dc.id,graph_dc[r.fr].bus_dc.id,r.Ifdc(graph_dc,1),1.0]
        Imk_dc.append(linha2)


    meas=Pinj_dc+Iinj_dc+Pkm_dc+Pmk_dc+Ikm_dc+Imk_dc+Vmod_dc


    
    dfDMEAS=pd.DataFrame(meas,columns=["type","from","to","zmeas","prec"])
    if flag_save_csv:
        dfDMEAS.to_csv(sys+"/DMEASdc_fp.csv",index=False,float_format="%.7f",header=True)
    return dfDMEAS




def save_DMEAS_conv_pf(convs_acdc,graph,graph_dc,sys,flag_save_csv=True):
    """
    Function to save the file with all DC measurements possible, from a DC power flow simulation.
    It uses the graph of the DC network to calculate every possible measurement and saves it in a file called
    DMEAS_fp.csv into the system's folder.
    @param: graph Graph structure with the information about the DC network
    @param: bran Dictionary with the information about the DC network branches
    @param: sys String with the system folder's name
    Note: This function is specifically designed for DC networks.

    200 - ACDC Converter internal filter bus active injection (p.u.) - virtual measurment it is a null injection
    201 - ACDC Converter internal filter bus reactive injection (p.u.) - virtual measurment it is a null injection
    202 - ACDC Converter internal transformer active power flow (p.u.) "para" field gives the direction (0 from grid to conv, 1 from conv to grid)
    203 - ACDC Converter internal transformer reactive power flow (p.u.) "para" field gives the direction (0 from grid to conv, 1 from conv to grid)
    220 - ACDC Converter internal reactor active power flow (p.u.) "para" field gives the direction (0 from grid to conv, 1 from conv to  
    230 - ACDC Converter internal reactor reactive power flow (p.u.) "para" field gives the direction (0 from grid to conv, 1 from conv to grid)
    204 - ACDC Converter internal filter bus voltage magnitude (p.u.) 
    205 - ACDC Converter internal filter bus voltage angle (rad)
    240 - ACDC Converter AC bus voltage magnitude (p.u.)
    250 - ACDC Converter AC bus voltage angle (rad)
    206 - ACDC Converter internal filter bus Current injection Re (p.u.) - virtual measurements (a null injection) 
    207 - ACDC Converter internal filter bus Current injection Im (p.u.) - virtual measurements (a null injection) 
    208 - ACDC Converter internal transformer Current flow Re (p.u.) "para" field gives the direction (0 from grid to conv, 1 from conv to grid)
    209 - ACDC Converter internal transformer Current flow Im (p.u.) "para" field gives the direction (0 from grid to conv, 1 from conv to grid)
    280 - ACDC Converter internal reactor Current flow Re (p.u.) "para" field gives the direction (0 from grid to conv, 1 from conv to grid)
    290 - ACDC Converter internal reactor Current flow Im (p.u.) "para" field gives the direction (0 from grid to conv, 1 from conv to grid)
    244 - ACDC Converter voltage ratio M = Vac/Vdc
    """


    meas=[] 

    Pinj=[]
    Qinj=[]
    Iinj_re=[]
    Iinj_im=[]


    Vm_f=[]
    Vangl_f=[]

    Vm_c=[]
    Vangl_c=[]

    Ptf=[] # active power flow in the transformer
    Qtf=[] # reactive power flow in the transformer
    Prc=[] # active power flow in the reactor
    Qrc=[] # reactive power flow in the reactor

    Itf_re=[] # active power flow in the transformer
    Itf_im=[] # reactive power flow in the transformer

    Irc_re=[] # active power flow in the reactor
    Irc_im=[] # reactive power flow in the reactor

    M=[]

    #calculates the Power Inejection (Reactive and Active)
    for conv in convs_acdc:
        if len(conv.d_inter_nodes) > 2:
            linha=[200,conv.id,-1,conv.d_inter_nodes[1].P(conv.d_inter_nodes),1]
            Pinj.append(linha)
            linha=[201,conv.id,-1,conv.d_inter_nodes[1].Q(conv.d_inter_nodes),1]
            Qinj.append(linha)
            linha=[206,conv.id,-1,conv.d_inter_nodes[1].I_inj_re(conv.d_inter_nodes),1]
            Iinj_re.append(linha)
            linha=[207,conv.id,-1,conv.d_inter_nodes[1].I_inj_im(conv.d_inter_nodes),1]
            Iinj_im.append(linha)
            linha=[204,conv.id,-1,conv.d_inter_nodes[1].V,1]
            Vm_f.append(linha)
            linha=[205,conv.id,-1,conv.d_inter_nodes[1].theta,1]
            Vangl_f.append(linha)
            linha=[240,conv.id,-1,conv.d_inter_nodes[2].V,1]
            Vm_c.append(linha)
            linha=[250,conv.id,-1,conv.d_inter_nodes[2].theta,1]
            Vangl_c.append(linha)
        elif len(conv.d_inter_nodes) == 2: # if there is no internal filter bus
            linha=[240,conv.id,-1,conv.d_inter_nodes[2].V,1] #TODO check if this work 
            Vm_c.append(linha)
            linha=[250,conv.id,-1,conv.d_inter_nodes[2].theta,1] #TODO check if this work
            Vangl_c.append(linha)
        else:
            pass # if there is no internal nodes, MMC converter not implemented yet 
        if conv.flag_trans==True:
            linha=[202,conv.id,0,conv.Ptf(0),1.0]
            Ptf.append(linha)
            linha=[203,conv.id,0,conv.Qtf(0),1.0]
            Qtf.append(linha)
            linha=[202,conv.id,1,conv.Ptf(1),1.0]
            Ptf.append(linha)
            linha=[203,conv.id,1,conv.Qtf(1),1.0]
            Qtf.append(linha)

            linha=[208,conv.id,0,conv.Itf_re(0),1.0]
            Itf_re.append(linha)
            linha=[209,conv.id,0,conv.Itf_im(0),1.0]
            Itf_im.append(linha)
            linha=[208,conv.id,1,conv.Itf_re(1),1.0]
            Itf_re.append(linha)
            linha=[209,conv.id,1,conv.Itf_im(1),1.0]
            Itf_im.append(linha)
        if conv.flag_reactor==True: # en train de faire 
            linha=[220,conv.id,0,conv.Prc(0),1.0]
            Prc.append(linha)
            linha=[230,conv.id,0,conv.Qrc(0),1.0]
            Qrc.append(linha)
            linha=[220,conv.id,1,conv.Prc(1),1.0]
            Prc.append(linha)
            linha=[230,conv.id,1,conv.Qrc(1),1.0]
            Qrc.append(linha)

            linha=[280,conv.id,0,conv.Irc_re(0),1.0]
            Irc_re.append(linha)
            linha=[290,conv.id,0,conv.Irc_im(0),1.0]
            Irc_im.append(linha)
            linha=[280,conv.id,1,conv.Irc_re(1),1.0]
            Irc_re.append(linha)
            linha=[290,conv.id,1,conv.Irc_im(1),1.0]
            Irc_im.append(linha)
        if 2 in conv.d_inter_nodes.keys():
            linha=[244,conv.id,-1,conv.d_inter_nodes[2].V/graph_dc[conv.i_busdc].Vdc,1.0]
            M.append(linha) # M = Vac/Vdc, Vac is the voltage in the AC bus and Vdc is the voltage in the DC bus






    meas=Pinj+Qinj+Iinj_re+Iinj_im+Vm_f+Vangl_f+Vm_c+Vangl_c+Ptf+Qtf+Itf_re+Itf_im+Prc+Qrc+Irc_re+Irc_im +M


    
    dfDMEAS=pd.DataFrame(meas,columns=["type","from","to","zmeas","prec"])
    if flag_save_csv:
        dfDMEAS.to_csv(sys+"/DMEASconv_fp.csv",index=False,float_format="%.7f",header=True)
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


def print_converter_info(conv_acdc):
    for conv in conv_acdc:
        print(f"Converter {getattr(conv, 'i', 'N/A')}:")
        print(f"  Pgrid: {getattr(conv, 'Pgrid', 'N/A')}")
        print(f"  Qgrid: {getattr(conv, 'Qgrid', 'N/A')}")
        print(f"  Pconv_ac: {getattr(conv, 'Pconv_ac', 'N/A')}")
        print(f"  Qconv_ac: {getattr(conv, 'Qconv_ac', 'N/A')}")
        print(f"  Ploss: {getattr(conv, 'Ploss', 'N/A')}")
        print(f"  Pdc: {getattr(conv, 'Pdc', 'N/A')}")
        print(f"  Iconv: {getattr(conv, 'Iconv', 'N/A')}")
        print("  Internal Nodes:")
        for k, node in getattr(conv, 'd_inter_nodes', {}).items():
            print(f"    Node {k}: V={getattr(node, 'V', 'N/A')}, theta={getattr(node, 'theta', 'N/A')}")
        print("-" * 40)
def print_ac_bus_voltages(graph):
    print("AC Bus Voltages:")
    for node in graph:
        V = getattr(node, 'V', None)
        theta = getattr(node, 'theta', None)
        print(f"  {node.bus.id}, {V},{theta}")

def print_dc_bus_voltages(graph_dc):
    print("\nDC Bus Voltages:")
    for node in graph_dc:
        Vdc = getattr(node, 'Vdc', None)
        print(f" {node.bus_dc.id}, {Vdc}")

def print_converter_internal_node_voltages(conv_acdc):
    print("Converter Internal Node Voltages:")
    for conv in conv_acdc:
        conv_id = getattr(conv, 'i', 'N/A')
        for k, node in getattr(conv, 'd_inter_nodes', {}).items():
            if k != 0:
                print(f"  {conv_id}, {k}, {getattr(node, 'V', 'N/A')},{getattr(node, 'theta', 'N/A')}")


def include_conv_in_injectioncac(graph, convs_acdc, dfDMEAS):
    """
    Updates the measurement DataFrame (`dfDMEAS`) by including the active (P) and reactive (Q) power injections
    from AC/DC converters (with either transformer or reactor) into the corresponding bus measurements.
    For each converter in `convs_acdc`, the function:
      - Checks if the converter is connected via a transformer or reactor.
      - Retrieves the power injections (P and Q) from the converter at time 0.
      - Identifies the corresponding bus in the `graph` and finds the matching measurement rows in `dfDMEAS`.
      - Adds the converter's P and Q injections to the "zmeas" column for the appropriate bus and measurement type.
      - Prints a warning if the converter's bus is not found in the measurement DataFrame or if the converter is not supported.
    Args:
        graph (list): List or mapping of bus objects, where each element provides access to a bus via `.bus.id`.
        convs_acdc (list): List of converter objects, each with attributes indicating connection type and methods to get P/Q injections.
        dfDMEAS (pandas.DataFrame): DataFrame containing measurement data with columns "type", "from", and "zmeas".
    Returns:
        None: The function modifies `dfDMEAS` in place.
    """

    for conv in convs_acdc:
        if conv.flag_trans == 1:
            Pgrid=conv.Ptf(0)
            Qgrid=conv.Qtf(0)
            bus_id = graph[conv.i_busac].bus.id
            maskP=(dfDMEAS["type"]==0) & (dfDMEAS["from"]==bus_id) 
            maskQ=(dfDMEAS["type"]==1) & (dfDMEAS["from"]==bus_id) 
            maskIre=(dfDMEAS["type"]==6) & (dfDMEAS["from"]==bus_id) 
            maskIim=(dfDMEAS["type"]==7) & (dfDMEAS["from"]==bus_id) 
            if not dfDMEAS[maskP].empty:
                dfDMEAS.loc[maskP, "zmeas"] += Pgrid
            else:
                print("Converter not in a bus")
            if not dfDMEAS[maskQ].empty:
                dfDMEAS.loc[maskQ, "zmeas"] += Qgrid
            else:
                print("Converter not in a bus")
            if not dfDMEAS[maskIre].empty:
                dfDMEAS.loc[maskIre, "zmeas"] += conv.Itf_re(0)
            else:
                print("Converter not in a bus")
            if not dfDMEAS[maskIim].empty:
                dfDMEAS.loc[maskIim, "zmeas"] += conv.Itf_im(0)
            else:
                print("Converter not in a bus")

        elif conv.flag_reactor == 1:
            Pgrid=conv.Prc(0)
            Qgrid=conv.Qrc(0)
            bus_id = graph[conv.i_busac].bus.id
            maskP=(dfDMEAS["type"]==0) & (dfDMEAS["from"]==bus_id) 
            maskQ=(dfDMEAS["type"]==1) & (dfDMEAS["from"]==bus_id) 
            maskIre=(dfDMEAS["type"]==6) & (dfDMEAS["from"]==bus_id) 
            maskIim=(dfDMEAS["type"]==7) & (dfDMEAS["from"]==bus_id) 
            if not dfDMEAS[maskP].empty:
                dfDMEAS.loc[maskP, "zmeas"] += Pgrid
            else:
                print("Converter not in a bus")
            if not dfDMEAS[maskQ].empty:
                dfDMEAS.loc[maskQ, "zmeas"] += Qgrid
            else:
                print("Converter not in a bus")
            if not dfDMEAS[maskIre].empty:
                dfDMEAS.loc[maskIre, "zmeas"] += conv.Irc_re(0)
            else:
                print("Converter not in a bus")
            if not dfDMEAS[maskIim].empty:
                dfDMEAS.loc[maskIim, "zmeas"] += conv.Irc_im(0)
            else:
                print("Converter not in a bus")
        else:
            print("Converter without a transformer or reactor, not supported yet") # TODO: converter without a transformer or reactor, not supported yet


def save_DMEAS_acdc(graph, bran, graph_dc, bran_dc, convs_acdc, sys, flag_save_csv=False):
    """
    Combines AC, DC, and converter measurement data into a single DataFrame for a hybrid AC/DC power system.
    This function collects measurement data from AC and DC networks, as well as from AC/DC converters,
    updates the AC measurements with converter injections, and concatenates all measurements into a single DataFrame.
    Optionally, the resulting DataFrame can be saved as a CSV file.
    Args:
        graph: The AC network graph object containing bus and branch data.
        bran: The AC branch data structure.
        graph_dc: The DC network graph object containing bus and branch data.
        bran_dc: The DC branch data structure.
        convs_acdc: The AC/DC converter data structure.
        sys (str): The system directory or identifier used for saving files.
        flag_save_csv (bool, optional): If True, saves the resulting DataFrame as a CSV file. Defaults to False.
    Returns:
        pandas.DataFrame: A DataFrame containing all AC, DC, and converter measurement data for the system.
    """
    
    
    dfDMEAS = save_DMEAS_ac_pf(graph, bran, sys, flag_save_csv=flag_save_csv)
    dfDMEAS_dc = save_DMEAS_dc_pf(graph_dc, bran_dc, sys, flag_save_csv=flag_save_csv)
    dfDMEAsconv = save_DMEAS_conv_pf(convs_acdc, graph, graph_dc, sys, flag_save_csv=flag_save_csv)
    include_conv_in_injectioncac(graph, convs_acdc, dfDMEAS)  # Update the measurements with converter injections
    #include converter in the buses injections

    dfDMEASACDC = pd.concat([dfDMEAS, dfDMEAS_dc, dfDMEAsconv], ignore_index=True)
    if flag_save_csv:
        dfDMEASACDC.to_csv(sys + "/DMEASacdc_fp.csv", index=False, float_format="%.7f", header=True)
    return dfDMEASACDC