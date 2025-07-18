from classes import *
from networkcalc import *
from SE import *
import numpy as np
import pandas as pd
from readfiles import *
import scipy.sparse.linalg as sliang 
import scipy.sparse as sparse 
import csv


def calc_dz_conv(vecZ,convs_acdc,dz):
    i=0
    for z in vecZ:
        dz[i]=z.dz_conv(convs_acdc)
        i=i+1


def create_z_x_pf_dc(graph_dc):
    zP=[]
    var_v={}
    i=0
    j=0
    for item in graph_dc:
        if item.bus_dc.type==1:
            mes=meas(item.id,-1,100,item.bus_dc.Pdc_conv+item.bus_dc.Pdc_gen-item.bus_dc.Pdc_load,1)
            zP.append(mes)
            var_v[item.id]=i
            i=i+1
    return zP,var_v


def Vinici_lf_dc(graph_dc,useDBUS_DC=1):
    '''
    Function to initate the voltages (state variables) for the load flow, 
    PQ buses recive 1 for the voltage module and 0 for the angle,
    PV recive the V from the DBUS for the module
    slack initate with the voltage from the DB 
    @param: graph list of instances of the node class with all the information about the network
    '''

    if useDBUS_DC==1:
        for node in graph_dc:
            node.Vdc=node.bus_dc.Vdc
    elif useDBUS_DC==0:
        for node in graph_dc:
            node.Vdc=1
    elif useDBUS_DC==2:
        pass


                


def power_flow_dc(graph_dc,prt=1,tol=1e-12,inici=1,itmax=20,printgrad=1,printres=1,printconv=1):
    """
    Function to run power flow calculation for a DC network. 
    @param graph dc with the informations of the network
    @param prt param to indicate if it prints anything, if it 0 nothing is printed
    @param tol tolerance of the load flow calculation
    @param inici intialization method of the variables if -1 it uses the DC power flow to intialize the angles and the X of the TCSC, 
    if it is 1 other value it uses DBAR for the PV voltage magnitudes and if it is 0, it initalizes with flat start
    """

    

    [z,var_v]=create_z_x_pf_dc(graph_dc)#create z and var_v and var_t for the traditional load flow


    Vinici_lf_dc(graph_dc,useDBUS_DC=inici)

    dz=np.zeros(len(z))
    H=np.zeros((len(z),len(var_v)))



    it=0
    conv=0
    lstdx=[]
    lstdz=[]


    while it<itmax:
    
        calc_dz(z,graph_dc,dz)
    
    
        calc_H_pf_dc(z,var_v,graph_dc,H)
    
    
        A=sparse.csc_matrix(H, dtype=float)
    
        dx=sliang.spsolve(A,dz)
    
        new_X_dc(graph_dc,var_v,dx)
    
        maxdx=np.max(np.abs(dx))
        maxdz=np.max(np.abs(dz))
    
        if (printgrad==1) & (prt==1):
            print("max dx {:e} | max dz {:e}  ".format(maxdx,maxdz))
        lstdx.append(maxdx)
        lstdz.append(maxdz)
        if maxdx< tol and maxdz < tol:
            conv=1
            if (printres==1) & (prt==1) :
                print("convergiu em {} itereacoes".format(it))
                prt_state_dc(graph_dc)
            break
            
        it=it+1
    
        if (printconv==1) & (prt==1):
            iterdict={"dx":lstdx,"dz":lstdz}
            df = pd.DataFrame(iterdict)
    
            # Save the DataFrame to a CSV file
            df.to_csv('conv.csv', index=False)
    return conv






def calc_H_pf_dc(z,var_v,gr_dc,H):
    i=0
    n_v=len(var_v)
    for item in z:
        soma1=0
        if item.type==100:
            #-------------------ramos fr branchs DC----------------------------------------#
            for key,bran_dc in gr_dc[item.k].adjk.items():# o branch entra com k-m e barra k é a variável
                if  gr_dc[item.k].bus_dc.type!=0:
                    soma1=soma1+bran_dc.dPfdVdc(gr_dc,0,item.k) # cacula dPkm/dtk
                if  bran_dc.to in var_v.keys():
                    H[i][var_v[bran_dc.to]]=bran_dc.dPfdVdc(gr_dc,0,bran_dc.to) #caclula dPkm/dtm to theta m na jacobiana
            for key,bran_dc in gr_dc[item.k].adjm.items(): # o branch entra com k-m e barra m é a variável
                if  gr_dc[item.k].bus_dc.type!=0:
                    soma1=soma1+bran_dc.dPfdVdc(gr_dc,1,item.k)  # calcula dpmk/dm
                if  bran_dc.fr in var_v.keys():
                    H[i][var_v[bran_dc.fr]]=bran_dc.dPfdVdc(gr_dc,1,bran_dc.fr) #faz calcula dPmk/dk
            if  gr_dc[item.k].bus_dc.type!=0:
                H[i][var_v[item.k]]=soma1
        i=i+1

        


def ini_Pgridslack(graph_dc,conv_acdc):
    """
    Initializes the P_grid attribute for slack converters in each DC area.
    This function calculates the net DC power balance (load minus generation) for each DC area,
    then assigns the required grid power (P_grid) to the slack converter in each area to balance the power.
    Args:
        graph_dc: A list or dictionary of DC bus nodes, each with attributes such as area, Pdc_load, Pdc_gen, and type.
        conv_acdc: A list of AC/DC converter objects, each with attributes such as i_busdc (index to graph_dc), P_grid, and possibly other converter parameters.
    Side Effects:
        Modifies the P_grid attribute of slack converters in-place to ensure power balance in each DC area.
    Notes:
        - The function assumes that each DC area has exactly one slack converter (type == 0).
        - The function expects that each converter in conv_acdc references its associated DC bus via i_busdc.
        - The function does not return any value; it updates objects in-place.
    """
        # Initializes P_grid for slack converters in each DC area to balance DC power.


    
    
    d_area={}
    d_area_slack={}

    for node in graph_dc:
        area=node.bus_dc.area
        if area not in d_area.keys():
            d_area[area]=0

        d_area[area]=d_area[area]+node.bus_dc.Pdc_load-node.bus_dc.Pdc_gen


    for conv in conv_acdc:
        area=graph_dc[conv.i_busdc].bus_dc.area
        if conv.type_dc!=0:
            d_area[area]=d_area[area]+conv.Pset
        else:
            d_area_slack[area]=conv

    
    for area in d_area.keys():
        d_area_slack[area].Pset=-d_area[area] #initial set point of the dc slack bus

def calc_conv_inter_pf(graph,graph_dc,conv_acdc,d_Pd,d_Qd):

    """
    Calculates and updates the internal electrical variables of AC/DC converters for power flow analysis.
    This function computes the internal node voltages, converter currents, and power quantities for each AC/DC converter
    in the system, based on the current power flow solution and converter parameters. It supports converters with either
    two or three internal nodes, handling the presence of transformers and/or reactors as appropriate. The function also
    updates the associated DC bus objects with the calculated DC power for each converter.
        graph (iterable): Dictionary representing the AC power system network, where each key is a bus index and each value
        graph_dc (iterable): Dictionary representing the DC network, where each key is a DC bus index and each value is an
                         object containing DC bus information.
        d_Pd (dict): Dictionary mapping AC bus indices to active power demand (delta P) at each bus with a converter.
        d_Qd (dict): Dictionary mapping AC bus indices to reactive power demand (delta Q) at each bus with a converter.
              angles, internal currents, and power quantities for their respective internal nodes. It also updates
              the DC bus objects in `graph_dc` with the calculated DC power for each converter.
    """
   
    j=complex(0,1)
    for conv in conv_acdc:
        #necessary only for the slack bus 
        
        if conv.type_ac==2: #reinforces the set points active and reactive power/
            Pgrid=conv.Pset
            Qgrid=conv.Qset
        if conv.type_ac==1: #reinforces the set points active power/
            Pgrid=conv.Pset
            if graph[conv.i_busac].bus.type==2:
                Qgrid=graph[conv.i_busac].Q(graph)+d_Qd[conv.i_busac]-graph[conv.i_busac].bus.Qg #caclulates the reactive power generated by the conveter when is PV mode
            else:
                Qgrid=0.000

        conv.Qgrid=Qgrid
        conv.Pgrid=Pgrid

        if graph[conv.i_busac].bus.type!=0: #if the converter is in the reactive bus 
            conv.Pgrid=conv.Pset 

        Sgrid=Pgrid+j*Qgrid #flowing iinto the grid (grid node)<---trafo----< filter/reactor
    
        Vgrid=graph[conv.i_busac].V*np.exp(j*graph[conv.i_busac].theta)

        Igrid=np.conj(Sgrid)/np.conj(Vgrid) #flowing iinto the grid (grid node)<---trafo----< filter/reactor

        if len(conv.d_inter_nodes)==3:
            Igrid2=Igrid/conv.d_inter_bran[0].tap #after trafo
            Vfilt=Vgrid+Igrid2/conv.d_inter_bran[0].ykm 
            conv.d_inter_nodes[1].V=np.abs(Vfilt)
            conv.d_inter_nodes[1].theta=np.angle(Vfilt) #after ideal trafo
            Iconv=Igrid2+j*Vfilt*conv.bf    
            Vconv=Vfilt+Iconv/conv.d_inter_bran[1].ykm
            conv.d_inter_nodes[2].V=np.abs(Vconv)
            conv.d_inter_nodes[2].theta=np.angle(Vconv)
        if len(conv.d_inter_nodes)==2:
            if 0 in conv.d_inter_bran.keys():
                Igrid2=Igrid/conv.d_inter_bran[0].tap#after trafo 
                Vconv=Vgrid+Igrid2/conv.d_inter_bran[0].ykm
                conv.d_inter_nodes[2].V=np.abs(Vconv)
                conv.d_inter_nodes[2].theta=np.angle(Vconv)
                Iconv=Igrid2+j*Vconv*conv.bf 
            elif 1 in conv.d_inter_bran.keys():
                Iconv=Igrid+j*Vconv*conv.conv.bf 
                Vconv=Vgrid+Igrid/conv.d_inter_bran[1].ykm
                conv.d_inter_nodes[2].V=np.abs(Vconv)
                conv.d_inter_nodes[2].theta=np.angle(Vconv)
                #current entering the converter
            else:
                OSError("converter without reactor or trafo")
        conv.Iconv=abs(Iconv)


        conv.Pconv_ac=np.real(Vconv*np.conj(Iconv)) #flowing out of the converter
        conv.Qconv_ac=np.imag(Vconv*np.conj(Iconv)) #flowing out of the converter
        
        conv.Ploss=conv.a+conv.Iconv*conv.b +conv.c*conv.Iconv**2


        conv.Pdc=-conv.Pconv_ac-conv.Ploss
        
        for conv in conv_acdc:
            bus_dc=conv.i_busdc
            graph_dc[bus_dc].bus_dc.Pdc_conv=conv.Pdc

def inc_conv_inj_acpf(graph,conv_acdc):
    """
    Updates the active (Pd) and reactive (Qd) power demands at AC buses in the graph to account for power injections from AC/DC converters.
    For each converter in conv_acdc, this function:
        - Stores the original Pd and Qd values for the associated AC bus.
        - Subtracts the converter's P_grid from the bus's Pd if the bus is of type 2 (PQ) or type 1 (PV).
        - Subtracts the converter's Q_grid from the bus's Qd if the bus is of type 1 (PV).
    Args:
        graph (iterable): A dictionary representing the power system network, where keys are bus indices and values are bus objects with attributes 'bus.Pd', 'bus.Qd', and 'bus.type'.
        conv_acdc (iterable): An iterable of converter objects, each with attributes 'i_busac' (the associated AC bus index), 'P_grid' (active power injection), and 'Q_grid' (reactive power injection).
    Returns:
        list: A list containing two dictionaries:
            - d_Pd: Original Pd values for each affected bus (keyed by bus index).
            - d_Qd: Original Qd values for each affected bus (keyed by bus index).
    """
    d_Pd={}
    d_Qd={}
    lst_Vctrl=[] #stores the buses whose V is controlled only by the converter
    #include Pgrid and Qgrid in the graph
    for conv in conv_acdc:
        d_Pd[conv.i_busac]=graph[conv.i_busac].bus.Pd #stores original loads
        d_Qd[conv.i_busac]=graph[conv.i_busac].bus.Qd #stores original loads
        if conv.type_ac==1:# if sets the point of active power injection  if the bus is a V control
            graph[conv.i_busac].bus.Pd=graph[conv.i_busac].bus.Pd-conv.Pset #includes the active power injection of the converter into the bus load
            if graph[conv.i_busac].bus.type==2:
                lst_Vctrl.append(conv.i_busac)
        if conv.type_ac==2:# sets the point for both active and reactive power injections if the bus is a PQ control
            graph[conv.i_busac].bus.Pd=graph[conv.i_busac].bus.Pd-conv.Pset #includes the active power injection of the converter into the bus load
            graph[conv.i_busac].bus.Qd=graph[conv.i_busac].bus.Qd-conv.Qset #includes the reactive power injection of the converter into the bus load
    return [d_Pd,d_Qd,lst_Vctrl]

def create_z_x_conv_powerflow(conv):
    """
    Creates measurement vector and variable mappings for DC slack bus iteratio .

    This function generates a list of pseudo-measurements (z) for the converter's internal nodes,
    and constructs dictionaries mapping internal node keys to indices for voltage magnitude (var_v)
    and angle (var_t) state variables. The measurements include active and reactive power flows
    at key points (e.g., converter, transformer, filter), and virtual measurements as needed for
    the converter's internal Newton-Raphson solution.

    Args:
        conv: Converter object with attributes for internal nodes, branches, and calculated powers.

    Returns:
        tuple:
            - z (list): List of measurement objects for the converter's internal power flow.
            - var_v (dict): Mapping from internal node keys to indices for voltage magnitude variables.
            - var_t (dict): Mapping from internal node keys to indices for voltage angle variables.
    """

    var_v={}
    var_t={}

    i=0
    
    for key, item in conv.d_inter_nodes.items():
        if key != 0 :
            var_t[key]=i
            var_v[key]=i
        i=i+1

    if 1 in conv.d_inter_nodes.keys(): # if the filter bus exists 
        measPconv=meas(conv.i,1,220,conv.Pconv_ac,0) # reactive power flow measurement in the reactor
        measQtrf=meas(conv.i,0,203,-conv.Qgrid,0) # reactive power flow measurement in the trafo
        measPvirt=meas(conv.i,0,200,0,0)
        measQvirt=meas(conv.i,0,201,0,0)
        z=[measPconv,measQtrf,measPvirt,measQvirt]
    elif 1 in conv.d_inter_bran.keys():
        measPconv=meas(conv.i,1,202,conv.Pconv_ac,0)
        measQtrf=meas(conv.i,0,203,-conv.Qgrid,0)
        z=[measPconv,measQtrf]
    else:
        measPconv=meas(conv.i,1,220,conv.Pconv_ac,0)
        measQtrf=meas(conv.i,0,230,-conv.Qgrid,0)
        z=[measPconv,measQtrf]

    return z,var_v,var_t

def calcH_conv_pf(z,var_t,var_v,conv_acdc,H):
    """
    Calculates the Jacobian matrix (H) for the converter's DC slack bus iteration.

    This function fills the matrix H with the partial derivatives of the measurement functions
    (active/reactive power flows at internal converter nodes and branches) with respect to the
    state variables (voltage angles and magnitudes) of the converter's internal nodes.

    Args:
        z (list): List of measurement objects for the converter's internal power flow.
        var_t (dict): Mapping from internal node keys to indices for voltage angle variables.
        var_v (dict): Mapping from internal node keys to indices for voltage magnitude variables.
        conv: Converter object containing internal node and branch data.
        H (np.ndarray): Preallocated Jacobian matrix to be filled in-place.

    Returns:
        None. The function updates the matrix H in-place.
    """
    
    i=0
    n_theta=len(var_t)
    b_filter=1
    b_conv=2
    b_grid=0
    for item in z:
        soma1=0
        soma2=0
        conv=conv_acdc[item.k]
        graph=conv.d_inter_nodes
        if item.type==200:
            for key,branch in graph[b_filter].adjk.items():# o branch entra com k-m e barra k é a variável
                soma1=soma1+branch.dPfdt(graph,0,b_filter) # cacula dPkm/dtk
                if branch.to in var_t.keys():
                    H[i][var_t[branch.to]]=branch.dPfdt(graph,0,branch.to) #caclula dPkm/dtm to theta m na jacobiana
            for key,branch in graph[b_filter].adjm.items(): # o branch entra com k-m e barra m é a variável
                soma1=soma1+branch.dPfdt(graph,1,b_filter)  # calcula dpmk/dm
                if  branch.fr in var_t.keys():
                    H[i][var_t[branch.fr]]=branch.dPfdt(graph,1,branch.fr) #faz calcula dPmk/dk
            if  graph[b_filter].bus.type!=0:
                H[i][var_t[b_filter]]=soma1
            soma1=0
            #-------------------ramos fr branchs normais e TCSC----------------------------------------#
            for key,branch in graph[b_filter].adjk.items(): # o branch entra com k-m e busra k é a variável
                if  graph[b_filter].bus.type!=0 and graph[b_filter].bus.type!=1:
                    soma2=soma2+branch.dPfdV(graph,0,b_filter) # calcula dPkm/dVk
                if  branch.to in var_v.keys():
                    H[i][var_v[branch.to]+n_theta]=branch.dPfdV(graph,0,branch.to) # calcula dPkm/dVm
            for key,branch in graph[b_filter].adjm.items():  # o branch entra com k-m e busra m é a variável
                if  graph[b_filter].bus.type!=0 and graph[b_filter].bus.type!=1:
                    soma2=soma2+branch.dPfdV(graph,1,b_filter) # Calcula dPmk/dm 
                if  branch.fr in var_v.keys():
                    H[i][var_v[branch.fr]+n_theta]=branch.dPfdV(graph,1,branch.fr) # Calcula dPmk/dk
            #-------------------ramos fr branchs UPFC----------------------------------------#
            if  graph[b_filter].bus.type!=0 and graph[b_filter].bus.type!=1 and (b_filter in var_v.keys()):
                H[i][var_v[b_filter]+n_theta]=soma2## Colocar as frrivadas do shunt
            soma2=0
        elif item.type==201:
            #-------------------ramos fr branchs normais e TCSC----------------------------------------#
            for key,branch in graph[b_filter].adjk.items(): # o branch entra com k-m e busra k é a variável
                if  graph[b_filter].bus.type!=0:
                    soma1=soma1+branch.dQfdt(graph,0,b_filter) # caclula dQkm/dtk
                if  branch.to in var_t.keys(): 
                    H[i][var_t[branch.to]]=branch.dQfdt(graph,0,branch.to) #caclula da dQkm/dtm
            for key,branch in graph[b_filter].adjm.items(): # o branch entra com k-m e busra m é a variável
                if  graph[b_filter].bus.type!=0:
                    soma1=soma1+branch.dQfdt(graph,1,b_filter)  #caclula dQmk/dtm
                if  branch.fr in var_t.keys():
                    H[i][var_t[branch.fr]]=branch.dQfdt(graph,1,branch.fr) #cacula dQmk/dk
            if  graph[b_filter].bus.type!=0:
                H[i][var_t[b_filter]]=soma1
            soma1=0
            #-------------------ramos fr branchs normais e TCSC----------------------------------------#
            for key,branch in graph[b_filter].adjk.items(): ## o branch entra com p-s e busra p é a variável (frrivadas modulo fr tensão)
                if  graph[b_filter].bus.type!=0 and graph[b_filter].bus.type!=1:
                    soma2=soma2+branch.dQfdV(graph,0,b_filter) #caclula dQkm/dVk
                if  branch.to in var_v.keys():
                    H[i][var_v[branch.to]+n_theta]=branch.dQfdV(graph,0,branch.to) #cacula dQkm/dVm
            for key,branch in graph[b_filter].adjm.items(): ## o branch entra com p-s e busra s é a variável (frrivadas modulo fr tensão)
                if  graph[b_filter].bus.type!=0 and graph[b_filter].bus.type!=1:
                    soma2=soma2+branch.dQfdV(graph,1,b_filter) # caclula dQmk/dVm
                if  branch.fr in var_v.keys():
                    H[i][var_v[branch.fr]+n_theta]=branch.dQfdV(graph,1,branch.fr) #cacula dQmk/dVk
            #-------------------ramos fr branchs UPFC----------------------------------------#
            if  graph[b_filter].bus.type!=0 and graph[b_filter].bus.type!=1 and (b_filter in var_v.keys()):
                if graph[b_filter].FlagBS==1:
                    soma2=soma2-2*graph[b_filter].Bs*graph[b_filter].V ## Colocar as frrivadas do shunt## Colocar as frrivadas do shunt## Colocar as frrivadas do shunt## Colocar as frrivadas do shunt
                H[i][var_v[b_filter]+n_theta]=soma2 # fazer o mesmo to as derivadas do upfc
            soma2=0
        elif (item.type==202) | (item.type==220):
            if item.type==202:
                bran=conv.d_inter_bran[0]
            elif item.type==220:
                bran=conv.d_inter_bran[1]

            if item.m==0: #Pkm k = grid and m = filt/conv
                k=bran.fr
                m=bran.to
                if k in var_t.keys():
                    H[i][var_t[k]]= bran.dPfdt(graph,0,k) #dPkm/dk
                if k in var_v.keys():
                    H[i][var_v[k]+n_theta]= bran.dPfdV(graph,0,k) #dPkm/dk
                if m in var_t.keys():
                    H[i][var_t[m]]= bran.dPfdt(graph,0,m) #dPkm/dm
                if m in var_v.keys():
                    H[i][var_v[m]+n_theta]= bran.dPfdV(graph,0,m) #dPkm/dm
            elif item.m==1: # entrou como k-m e a barra k é na verdade a m
                k=bran.to
                m=bran.fr
                if k in var_t.keys():
                    H[i][var_t[k]]= bran.dPfdt(graph,1,k) # dPmk/dm
                if k in var_v.keys():
                    H[i][var_v[k]+n_theta]= bran.dPfdV(graph,1,k) # dPmk/dm
                if m in var_t.keys():
                    H[i][var_t[m]]= bran.dPfdt(graph,1,m) # dPmk/dk
                if m in var_v.keys():
                    H[i][var_v[m]+n_theta]= bran.dPfdV(graph,1,m) # dPmk/dk
        elif (item.type==203) | (item.type==230):
            if item.type==203:
                bran=conv.d_inter_bran[0]
            elif item.type==230:
                bran=conv.d_inter_bran[1]

            if item.m==0: #Pkm k = grid and m = filt/conv
                k=bran.fr
                m=bran.to
                if k in var_t.keys():
                    H[i][var_t[k]]= bran.dQfdt(graph,0,k) #dPkm/dk
                if k in var_v.keys():
                    H[i][var_v[k]+n_theta]= bran.dQfdV(graph,0,k) #dPkm/dk
                if m in var_t.keys():
                    H[i][var_t[m]]= bran.dQfdt(graph,0,m) #dPkm/dm
                if m in var_v.keys():
                    H[i][var_v[m]+n_theta]= bran.dQfdV(graph,0,m) #dPkm/dm
            elif item.m==1: # entrou como k-m e a barra k é na verdade a m
                k=bran.to
                m=bran.fr
                if k in var_t.keys():
                    H[i][var_t[k]]= bran.dQfdt(graph,1,k) # dPmk/dm
                if k in var_v.keys():
                    H[i][var_v[k]+n_theta]= bran.dQfdV(graph,1,k) # dPmk/dm
                if m in var_t.keys():
                    H[i][var_t[m]]= graph[k].bran.dQfdt(graph,1,m) # dPmk/dk
                if m in var_v.keys():
                    H[i][var_v[m]+n_theta]= bran.dQfdV(graph,1,m) # dPmk/dk
        i=i+1

def new_X_conv_pf(conv,var_t,var_v,dx):
    """
    Updates the voltage angles (theta) and magnitudes (V) of converter nodes.
    Parameters:
        conv: An object containing the converter's internal 
        var_t (dict): A dictionary mapping node keys to indices for voltage angles (theta).
        var_v (dict): A dictionary mapping node keys to indices for voltage magnitudes (V).
        dx (list or array-like): A vector of incremental updates for state variables, where the first n_theta elements correspond to theta updates and the remaining elements correspond to V updates.
    Side Effects:
        Modifies the 'theta' and 'V' attributes of nodes in conv.d_inter_nodes in-place, applying the corresponding increments from dx.
    Notes:
        - Assumes that the order and length of dx matches the combined size of var_t and var_v.
        - The function does not return any value; it updates the graph in-place.
    """
    
    graph=conv.d_inter_nodes
    n_theta=len(var_t)
    for key,item in var_t.items():
        graph[key].theta=graph[key].theta+dx[item]
    for key,item in var_v.items():
        graph[key].V=graph[key].V+dx[item+n_theta]

def conv_intern_Pf(conv_acdc,i_conv,tol=1e-8):
    """
    Performs the internal power flow calculation for a converter using the Newton-Raphson method.
    This function iteratively solves the converter's power flow equations (from Berteens,2012 paper ) by updating the state variables
    until the solution converges within a specified tolerance or a maximum number of iterations is reached.
    Args:
        conv: Converter data structure containing parameters and state variables.
        tol (float, optional): Convergence tolerance for the Newton-Raphson method. Defaults to 1e-8.
    Returns:
        int: 1 if the solution converged within the tolerance, 0 otherwise.
    """


    [z,var_v,var_t]=create_z_x_conv_powerflow(conv_acdc[i_conv])

    dz=np.zeros(len(z))
    H=np.zeros((len(z),len(var_t)+len(var_v)))
    it=0

    div=0
    while (it<10):
        calc_dz_conv(z,conv_acdc,dz)

        calcH_conv_pf(z,var_t,var_v,conv_acdc,H)

        dx=np.linalg.solve(H,dz)

        new_X_conv_pf(conv_acdc[i_conv],var_t,var_v,dx)
        it=it+1

        if np.linalg.norm(dx)<tol:
            div=1
            break

    return div
    
def slack_bus_it(conv_acdc,graph_dc,graph,dPd,tol=1e-8):

    """
    Iterates over slack buses in an AC/DC power system to update power balances and enforce DC slack bus conditions on AC networks.
    This function identifies slack buses among the DC converters, updates their associated AC bus power injections,
    and checks for convergence by comparing the calculated and expected grid power. It is typically used within
    iterative power flow algorithms for hybrid AC/DC networks.
    Args:
        conv_acdc (list): List of converter objects representing AC/DC converters in the system.
        graph_dc (list): List of DC bus objects or nodes in the DC network graph.
        graph (list): List of AC bus objects or nodes in the AC network graph.
        dPd (dict): Dict or array of original active power demands at each AC bus.
        tol (float, optional): Tolerance for convergence checking. Default is 1e-8.
    Returns:
        list: List of absolute differences between calculated and expected slack bus power injections.
                Returns [-1] if a divergence is detected during the iteration.
    """

    d_area_slack={}
    for i in range(len(conv_acdc)):
        if conv_acdc[i].type_dc==0: #is a slack bus
            d_area_slack[graph_dc[conv_acdc[i].i_busdc].bus_dc.area]=(conv_acdc[i].i_busac,i)
            conv_acdc[i].Pconv_ac = - graph_dc[conv_acdc[i].i_busdc].Pdc(graph_dc) - conv_acdc[i].Ploss
    
    dz_Pslack=[]
    for key in d_area_slack.keys(): 
        
        i_busac=d_area_slack[key][0]
        i_conv=d_area_slack[key][1]


        div = conv_intern_Pf(conv_acdc,i_conv)

        if div==0:
            print("converter slack bus iteration divergence")
            return [-1] 

        if 0 in conv_acdc[i_conv].d_inter_bran.keys(): #caculates the set point of the slack bus
            Pset=-conv_acdc[i_conv].Ptf(0)
        else:
            Pset=-conv_acdc[i_conv].Prc(0)
        
        dz_Pslack.append(abs(conv_acdc[i_conv].Pset-Pset))

        conv_acdc[i_conv].Pset=Pset
        graph[conv_acdc[i_conv].i_busac].bus.Pd=dPd[conv_acdc[i_conv].i_busac]-conv_acdc[i_conv].Pset

    return dz_Pslack

def power_flow_iterative(graph,graph_dc,conv_acdc,tol=1e-8,prt=1,printconv=1,printres=1):
    """
    Runs a sequential AC/DC power flow algorithm for hybrid AC/DC grids, similar to the implementation described in 
    J. Beerten, S. Cole and R. Belmans, "Generalized Steady-State VSC MTDC Model for Sequential AC/DC Power Flow Algorithms," 
    IEEE Transactions on Power Systems. 2012
    This function iteratively solves the AC and DC power flows, updating converter injections and slack bus conditions 
    until convergence is achieved or a maximum number of iterations is reached.
    # NOTE: Droop control for DC voltage regulation is not yet implemented in this routine.
    #       Also, converters without transformer or reactor branches (i.e., direct AC/DC coupling)
    #       are not currently supported in the internal converter modeling and power flow.
    #       These features should be added for full generality in future development.
    Args:
        graph (dict): Data structure representing the AC network, with buses and branches.
        graph_dc (dict): Data structure representing the DC network, with nodes and branches.
        conv_acdc (list): List of AC/DC converter objects or data structures.
        tol (float, optional): Convergence tolerance for the iterative process. Default is 1e-8.
        prt (int, optional): Flag to control printing of iteration progress. Default is 1.
        printconv (int, optional): Flag to control printing of convergence information. Default is 1.
        printres (int, optional): Flag to control printing of final results. Default is 1.
    Returns:
        None. Prints results and convergence information to the console.
    Raises:
        Prints a message and returns if AC or DC power flow fails to converge.
    """



    ini_Pgridslack(graph_dc,conv_acdc) #initialize the AC buses connected to convters that are connected to DC slack buses
    [d_Pd,d_Qd,lst_Vctrl]=inc_conv_inj_acpf(graph,conv_acdc) # includes Pgrid and Qgrid in the graph demand of AC buses and stores original loads in d_Pd and d_Qd

    it=0
    ini=1
    tol=1e-8
    while(it<10):
        if it>0:
            ini=2

        for i in lst_Vctrl:
            graph[i].bus.type=1 #sets the bus type to PV for the next power flow iteration
            
        div=power_flow(graph,inici=ini,prt=0,itmax=20,tol=tol) #calculates AC power flow with the Pgrid and Qgrid reflected as loads

        for i in lst_Vctrl:
            graph[i].bus.type=2 #sets the bus type to PQ for the next power flow iteration
        
        if div==0:
            print("AC power flow divergence")
            return

        calc_conv_inter_pf(graph,graph_dc,conv_acdc,d_Pd,d_Qd) #using AC power flow results calculates the dc injections for the dc power flows

        div=power_flow_dc(graph_dc,prt=0,tol=tol,inici=ini,itmax=20,printgrad=1,printres=1) # calculates the DC power flows
        if div==0:
            print("DC power flow divergence")
            return
        
        dzP=slack_bus_it(conv_acdc,graph_dc,graph,d_Pd,tol=tol) # calculates the 
        if np.linalg.norm(dzP)<tol:
            print("Conv in {} iterations".format(it))
            print("AC result")
            prt_state(graph,flag_radians=1)
            print("DC result")
            prt_state_dc(graph_dc)
            break
        it=it+1
        if(prt==1): 
            print("Slack bus iteration dz {:.2e}, it: {:d}".format(np.linalg.norm(dzP),it))