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
import numpy as np


def include_conv_nodes_in_graph(graph,ind_i, bran, convs_acdc):
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
            if key != 0:  # it is not the grid bus, already in the graph
                new = node_graph(nac_nodes, node.bus)
                new.V = node.V
                new.theta = node.theta
                graph.append(new)
                dnew_i[key] = nac_nodes
                if key == 2:
                    conv.i_busconv = nac_nodes
                else:
                    conv.i_busfilter = nac_nodes
                    new.FlagBS=1
                    new.Bs = node.Bs
                ind_i[node.bus.id] = nac_nodes
                nac_nodes += 1
            else:
                dnew_i[key] = conv.i_busac
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
            graph[dnew_i[br.to]].adjm.update({key_str:item})
            graph[dnew_i[br.to]].ladjm.append(dnew_i[br.fr])
            nac_bran += 1

def create_z_se_conv(dfDMEAS, convs_acdc, ind_id_conv):

    dconvtyp_actype = {
    200: 0, 201: 1, 202: 2, 203: 3, 204: 4, 205: 5, 240: 4, 250: 5,
    202: 2, 203: 3, 220: 2, 230: 3, 206: 6, 207: 7, 208: 8, 209: 9,
    280: 8, 290: 9
    }
    mask = (dfDMEAS["type"] > 199) & (dfDMEAS["type"] < 300)

    z_Conv = []
    for idx, row in dfDMEAS[mask].iterrows():
        conv = convs_acdc[ind_id_conv[int(row["from"])]]
        if int(row["type"]) in [200, 201, 204, 205, 206, 207]:  # filter bus measurements        
            m = meas(conv.i_busfilter, -1, dconvtyp_actype[int(row["type"])], row["zmeas"], row["prec"])
        elif int(row["type"]) in [240, 250]:  # converter bus measurements
            m = meas(conv.i_busconv, -1, dconvtyp_actype[int(row["type"])], row["zmeas"], row["prec"])
        elif int(row["type"]) in [202, 203, 208, 209]:  # transformer internal flows (power and current)
            external = conv.i_busac
            internal = conv.i_busfilter if conv.flag_reactor == 1 else conv.i_busconv
            (from_bus, to_bus) = (external, internal) if int(row["to"]) == 0 else (internal, external)
            m = meas(from_bus, to_bus, dconvtyp_actype[int(row["type"])], row["zmeas"], row["prec"])
        elif int(row["type"]) in [220, 230, 280, 290]:  # reactor internal flows (power and current) 
            internal = conv.i_busconv
            external = conv.i_busfilter if conv.flag_trans == 1 else conv.i_busconv
            (from_bus, to_bus) = (external, internal) if int(row["to"]) == 0 else (internal, external)
            m = meas(from_bus, to_bus, dconvtyp_actype[int(row["type"])], row["zmeas"], row["prec"])
        else:
            print("type not recognized: ", int(row["type"]))
        z_Conv.append(m)
    return z_Conv




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

include_conv_nodes_in_graph(graph,ind_i, bran, convs_acdc)

#%%
# Remove specific measurements from the graph
# Example: Remove measurements with type == 201 (change as needed)

types_to_remove = [
206,    
207]
mask_remove = dfDMEAS["type"].isin(types_to_remove) 
mask_remove2 = dfDMEAS["from"].isin([1,2]) 
dfDMEAS = dfDMEAS[(mask_remove & mask_remove2)].reset_index(drop=True)

prec_virtual=1e-6
timax=30
printcond=0
printmat=0
printgrad=True
printres=True
tol=1e-6
tol2=1e-6

# ACDC converter internal measurements

[z_ac,var_t,var_v]=create_z_x_se_ac(graph, dfDMEAS, ind_i)
z_conv = create_z_se_conv(dfDMEAS, convs_acdc, ind_id_conv)
[z_dc,var_vdc]=create_z_x_dc_se(graph_dc, dfDMEAS, ind_i_dc)
#create losses constraints

Hac=np.zeros((len(z_ac)+len(z_conv), len(var_t)+len(var_v)))

#%%

n_teta=len(var_t)
n_v=len(var_v)
n_vdc=len(var_vdc)
dz=np.zeros(len(z_ac)+len(z_conv))
z=z_ac + z_conv
W=create_W(z,mode=2,prec_virtual=prec_virtual) 
lstdx=[]
lstdz=[]
#%%
it=0
it2=0
a=1
conv=0
Vinici(graph,flatStart=7,ind_i=ind_i)

while(it <1):

    calc_dz(z,graph,dz)
    calc_H_EE(z,var_t,var_v,graph,Hac)


    grad=np.matmul(np.matmul(Hac.T,W),dz)

    try: 
        dx=NormalEQ_QR(Hac,W,dz,printcond=printcond,printmat=printmat)
    except:
        conv=0
        it=30
        break

    Jxk=np.matmul(np.matmul(dz,W),dz)
    if it==0:
        norminicial=liang.norm(grad) if liang.norm(grad) > 1e-10 else 1



    new_X(graph,var_t,var_v,a*dx)
    

    it=it+1
    if printgrad==True:
        print("{:e},{:e}".format( liang.norm(grad)/norminicial,liang.norm(a*dx)))
    
    gradredux=liang.norm(grad)/norminicial
    maxdx= liang.norm(a*dx)
    lstdx.append(maxdx)
    lstdz.append(gradredux)
    
    if maxdx>1e5:
        conv=0
        it=30
        break
    if gradredux <tol2 and maxdx<tol:
        txt="Conv in {:d} iterations".format(it)
        if printres==True:
            print(liang.norm(grad)/norminicial)
            print(txt)
            prt_state(graph)
        conv=1
        break


# %%
