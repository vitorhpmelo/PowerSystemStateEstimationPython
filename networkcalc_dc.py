from classes import *
from SE import *
import numpy as np
import pandas as pd
from readfiles import *
import scipy.sparse.linalg as sliang 
import scipy.sparse as sparse 
import csv



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

        
