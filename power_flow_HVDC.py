#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%
from classes import *
from readfiles import *
from networkstruc import *
from SE import *
from meas_sampl import *
import pandas as pd
import numpy as np
from networkcalc import *
from networkcalc_dc import *
from BadData import *
import numpy.linalg as liang
import scipy.sparse.linalg as sliang 


def add_conv_inter_nodes_to_graph(graph, bran, convs_acdc):
    """
    Adds converter interface nodes and branches to the power system graph.
    This function iterates over a list of AC/DC converter objects, adding their
    internal nodes and branches to the provided graph and branch dictionaries.
    For each converter, it creates new node and branch objects as needed,
    updates their properties, and maps the new nodes inside the converters.
    Args:
        graph (list): List of node objects representing the power system buses.
        bran (dict): Dictionary of branch objects representing the system branches.
        convs_acdc (list): List of converter objects, each containing internal nodes
            (d_inter_nodes) and branches (d_inter_bran) to be added to the graph.
    Side Effects:
        Modifies the `graph` list and `bran` dictionary in place by adding new nodes
        and branches corresponding to the converter interfaces.
    Notes:
        - Assumes that node_graph and branch constructors, as well as methods like
          cykm() and twoPortCircuit(), are defined elsewhere.
        - Updates converter attributes (i_busconv, i_busfilter) to reflect new node indices.
        - Maintains adjacency information for each node in the graph.
    """
    
    nac_nodes = len(graph)
    nac_bran = len(bran)

    for conv in convs_acdc:
        dnew_i = {}
        for (key, node) in conv.d_inter_nodes.items():
            dnew_i[key] = conv.i_busac
            if key != 0:  # it is not the grid bus, already in the graph
                new = node_graph(nac_nodes, node.bus)
                new.V = node.V
                new.theta = node.theta
                new.Bs = node.Bs
                graph.append(new)
                dnew_i[key] = nac_nodes
                if key == 2:
                    conv.i_busconv = nac_nodes
                else:
                    conv.i_busfilter = nac_nodes
                nac_nodes += 1
        for (key, br) in conv.d_inter_bran.items():
            key_str = str(dnew_i[br.fr]) + "-" + str(dnew_i[br.to])
            item = branch(br.id, dnew_i[br.fr], dnew_i[br.to], br.type, nac_bran)
            item.x = br.x
            item.r = br.r
            item.bsh = br.bsh  # divides the shunt suceptance by two
            item.tap = br.tap
            item.cykm()  # calculates the ykm
            item.twoPortCircuit()  # creates the two port circuit
            bran[key_str] = item
            graph[dnew_i[br.fr]].adjk.update({key_str: item})
            graph[dnew_i[br.fr]].ladjk.append(dnew_i[br.to])
            graph[dnew_i[br.to]].adjm.update({key_str: item})
            graph[dnew_i[br.to]].ladjm.append(dnew_i[br.fr])
            nac_bran += 1






sys="case5_2grids"

dfDBUS,dfDBRAN,dfDMEAS,dfDFACTS=read_files(sys)

dfDBUS_dc, dfDBRAN_dc, dfDCONV_acdc= read_files_DC(sys)




#%% network building
[bus,nbus,pv,pq,ind_i]=create_bus(dfDBUS)
[bran,nbran]=create_bran(dfDBRAN,ind_i)


[bus_dc,nbus_dc,slack,ind_i_dc]=create_bus_dc(dfDBUS_dc)

[bran_dc,nbran_dc]=create_bran_dc(dfDBRAN_dc,ind_i_dc)


[convs_acdc,nconv,ind_id_conv]=create_conv_acdc(dfDCONV_acdc,ind_i_dc,ind_i)

graph=create_graph(bus,bran)
graph_dc=create_graph_dc(bus_dc,bran_dc)

add_conv_acdc_ingraph(graph,graph_dc,convs_acdc)
#%%



power_flow_iterative(graph,graph_dc,convs_acdc)



dfDMEAS=save_DMEAS_acdc(graph,bran, graph_dc, bran_dc, convs_acdc, sys)
# %%



#%%
