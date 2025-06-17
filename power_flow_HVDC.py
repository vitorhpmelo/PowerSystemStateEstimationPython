#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%
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
        
        Sgrid=Pgrid+j*Qgrid #flowing iinto the grid (grid node)<---trafo----< filter/reactor
    
        Vgrid=graph[conv.i_busac].V*np.exp(j*graph[conv.i_busac].theta)

        Igrid=np.conj(Sgrid)/np.conj(Vgrid) #flowing iinto the grid (grid node)<---trafo----< filter/reactor

        if len(conv.d_inter_nodes)==3:
            Igrid2=Igrid/conv.d_inter_bran["tr"].tap #after trafo
            Vfilt=Vgrid+Igrid2/conv.d_inter_bran["tr"].ykm 
            conv.d_inter_nodes["f"].V=np.abs(Vfilt)
            conv.d_inter_nodes["f"].theta=np.angle(Vfilt) #after ideal trafo
            Iconv=Igrid2+j*Vfilt*conv.bf    
            Vconv=Vfilt+Iconv/conv.d_inter_bran["rc"].ykm
            conv.d_inter_nodes["c"].V=np.abs(Vconv)
            conv.d_inter_nodes["c"].theta=np.angle(Vconv)
        if len(conv.d_inter_nodes)==2:
            if "tr" in conv.d_inter_bran.keys():
                Igrid2=Igrid/conv.d_inter_bran["tr"].tap#after trafo 
                Vconv=Vgrid+Igrid2/conv.d_inter_bran["tr"].ykm
                conv.d_inter_nodes["c"].V=np.abs(Vconv)
                conv.d_inter_nodes["c"].theta=np.angle(Vconv)
                Iconv=Igrid2+j*Vconv*conv.bf 
            elif "rc" in conv.d_inter_bran.keys():
                Vconv=Vgrid+Igrid/conv.d_inter_bran["rc"].ykm
                conv.d_inter_nodes["c"].V=np.abs(Vconv)
                conv.d_inter_nodes["c"].theta=np.angle(Vconv)
                Iconv=Igrid+j*Vconv*conv.conv.bf #current entering the converter
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
