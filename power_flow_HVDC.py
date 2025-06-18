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
from networkcalc_dc import *
from BadData import *
import numpy.linalg as liang
import scipy.sparse.linalg as sliang 



def ini_Pgridslack(graph,graph_dc,conv_acdc):
    
    
    d_area={}
    d_area_slack={}

    for node in graph_dc:
        area=node.bus_dc.area
        if area not in d_area.keys():
            d_area[area]=0

        d_area[area]=d_area[area]+node.bus_dc.Pdc_load-node.bus_dc.Pdc_gen


    for conv in conv_acdc:
        area=graph_dc[conv.i_busdc].bus_dc.area
        if graph_dc[conv.i_busdc].bus_dc.area not in d_area.keys():
            d_area[area]=0
        if graph_dc[conv.i_busdc].bus_dc.type==1:
            d_area[area]=d_area[area]+conv.P_grid
        if graph_dc[conv.i_busdc].bus_dc.type==0:
            d_area_slack[area]=conv


    for area in d_area.keys():
        d_area_slack[area].P_grid=-d_area[area]


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
        Pgrid=graph[conv.i_busac].P(graph)+d_Pd[conv.i_busac]-graph[conv.i_busac].bus.Pg
        Qgrid=graph[conv.i_busac].Q(graph)+d_Qd[conv.i_busac]-graph[conv.i_busac].bus.Qg
        
        conv.Pgrid=Pgrid
        conv.Qgrid=Qgrid
        
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

    #include Pgrid and Qgrid in the graph
    for conv in conv_acdc:
        d_Pd[conv.i_busac]=graph[conv.i_busac].bus.Pd
        d_Qd[conv.i_busac]=graph[conv.i_busac].bus.Qd
        if graph[conv.i_busac].bus.type==1 or graph[conv.i_busac].bus.type==2:
            graph[conv.i_busac].bus.Pd=graph[conv.i_busac].bus.Pd-conv.P_grid
        if graph[conv.i_busac].bus.type==2:
            graph[conv.i_busac].bus.Qd=graph[conv.i_busac].bus.Qd-conv.Q_grid

    return [d_Pd,d_Qd]

def create_z_x_conv_powerflow(conv):

    var_v={}
    var_t={}

    i=0
    
    for key, item in conv.d_inter_nodes.items():
        if key != 0 :
            var_t[key]=i
            var_v[key]=i
        i=i+1

    if 1 in conv.d_inter_nodes.keys(): # if the filter bus exists 
        measPconv=meas(i_conv,1,220,conv.Pconv_ac,0) # reactive power flow measurement in the reactor
        measQtrf=meas(i_conv,0,203,-conv.Qgrid,0) # reactive power flow measurement in the trafo
        measPvirt=meas(i_conv,0,200,0,0)
        measQvirt=meas(i_conv,0,201,0,0)
        z=[measPconv,measQtrf,measPvirt,measQvirt]
    elif 1 in conv.d_inter_bran.keys():
        measPconv=meas(i_conv,1,202,conv.Pconv_ac,0)
        measQtrf=meas(i_conv,0,203,-conv.Qgrid,0)
        z=[measPconv,measQtrf]
    else:
        measPconv=meas(i_conv,1,220,conv.Pconv_ac,0)
        measQtrf=meas(i_conv,0,230,-conv.Qgrid,0)
        z=[measPconv,measQtrf]

    return z,var_v,var_t

def calcH_conv_pf(z,var_t,var_v,conv,H):
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
    graph=conv.d_inter_nodes
    n_theta=len(var_t)
    for key,item in var_t.items():
        graph[key].theta=graph[key].theta+dx[item]
    for key,item in var_v.items():
        graph[key].V=graph[key].V+dx[item+n_theta]

sys="case5_2grids"


dfDBUS,dfDBRAN,dfDMEAS,dfDFACTS=read_files(sys)

dfDBUS_dc, dfDBRAN_dc, dfDCONV_acdc= read_files_DC(sys)

# %%

[bus,nbus,pv,pq,ind_i]=create_bus(dfDBUS)
[bran,nbran]=create_bran(dfDBRAN,ind_i)


[bus_dc,nbus_dc,slack,ind_i_dc]=create_bus_dc(dfDBUS_dc)

[bran_dc,nbran_dc]=create_bran_dc(dfDBRAN_dc,ind_i_dc)


[conv_acdc,nconv,ind_id_conv]=create_conv_acdc(dfDCONV_acdc,ind_i_dc,ind_i)
#%%

graph=create_graph(bus,bran)
graph_dc=create_graph_dc(bus_dc,bran_dc)

addACDCconv_ingraph(graph,graph_dc,conv_acdc)
#%%

for conv in conv_acdc:
    conv.create_internal_network(graph)
#%%

ini_Pgridslack(graph,graph_dc,conv_acdc)

#%%

[d_Pd,d_Qd]=inc_conv_inj_acpf(graph,conv_acdc)

    

#%%


conv=power_flow(graph,inici=1,prt=1,itmax=20)



#%%
              
calc_conv_inter_pf(graph,graph_dc,conv_acdc,d_Pd,d_Qd)


#%%
power_flow_dc(graph_dc,prt=1,tol=1e-12,inici=1,itmax=20,printgrad=1,printres=1)

# %% Slack bus iteration


d_area_slack={}
for i in range(len(conv_acdc)):
    if graph_dc[conv_acdc[i].i_busdc].bus_dc.type==0: #is a slack bus
        d_area_slack[graph_dc[conv_acdc[i].i_busdc].bus_dc.area]=(conv_acdc[i].i_busac,i)
        conv_acdc[i].Pconv_ac = - graph_dc[conv_acdc[i].i_busdc].Pdc(graph_dc) - conv_acdc[i].Ploss
# %%  determines 

i_busac=d_area_slack[1][0]
i_conv=d_area_slack[1][1]

conv=conv_acdc[i_conv]

#%%
[z,var_v,var_t]=create_z_x_conv_powerflow(conv)


# %% create z and x for conv 
dz=np.zeros(len(z))
H=np.zeros((len(z),len(var_t)+len(var_v)))

#%% create z and var power flow

it=0
lstdx=[]
lstdz=[]

while (it<2):

    calc_dz_conv(z,conv_acdc,dz)

    calcH_conv_pf(z,var_t,var_v,conv,H)


    dx=np.linalg.solve(H,dz)


    new_X_conv_pf(conv,var_t,var_v,dx)
    it=it+1

# %%
