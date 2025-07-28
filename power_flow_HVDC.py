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


def SE_WLS_acdc(graph, graph_dc, convs_acdc, dfDMEAS, ind_i, ind_i_dc, ind_id_conv, prec_virtual=1e-6,scale_virt=0.1, printcond=0, printmat=0, printgrad=True, printres=True, tol=1e-6, tol2=1e-6, itmax=20):
    """
    Performs Weighted Least Squares (WLS) State Estimation for hybrid AC/DC power systems.
    This function estimates the state variables (voltages, angles, etc.) of a power system that includes both AC and DC networks, as well as AC/DC converters internal voltages.
    Args:
        graph: The AC network graph object containing buses, branches, and system topology.
        graph_dc: The DC network graph object containing DC nodes and topology.
        convs_acdc: List or structure containing AC/DC converter information.
        dfDMEAS: DataFrame or structure containing measurement data for both AC and DC systems.
        ind_i: Indices or identifiers for AC nodes/buses.
        ind_i_dc: Indices or identifiers for DC nodes.
        ind_id_conv: Indices or identifiers for converter nodes.
        prec_virtual (float, optional): Precision parameter for virtual measurements. Default is 1e-6.
        scale_virt (float, optional): Scaling factor for virtual measurements. Default is 0.1.
        printcond (int, optional): Flag to print condition number information. Default is 0.
        printmat (int, optional): Flag to print matrix information. Default is 0.
        printgrad (bool, optional): Flag to print gradient information during iterations. Default is True.
        printres (bool, optional): Flag to print results upon convergence. Default is True.
        tol (float, optional): Tolerance for maximum state variable update (dx) for convergence. Default is 1e-6.
        tol2 (float, optional): Tolerance for normalized gradient for convergence. Default is 1e-6.
        itmax (int, optional): Maximum number of iterations. Default is 20.
    Returns:
        conv (int): Convergence flag (1 if converged, 0 otherwise).
        lstdx (list): List of maximum state variable updates (dx) per iteration.
        lstdz (list): List of normalized gradient values per iteration.
    Raises:
        Exception: If the normal equations cannot be solved (e.g., due to singularity).
    Functionality:
        - Initializes state variables for AC and DC networks.
        - Constructs measurement vectors and Jacobian matrices for AC, DC, and converter measurements.
        - Iteratively solves the WLS normal equations using QR decomposition.
        - Updates state variables and checks for convergence.
        - Handles virtual measurements and constraints for improved observability.
        - Prints diagnostic information if requested.
    """

    # ACDC converter internal measurements
    

    [z_ac, var_t, var_v] = create_z_x_se_ac(graph, dfDMEAS, ind_i)
    z_conv = create_z_se_conv(dfDMEAS, convs_acdc, ind_id_conv)

    c_conv = create_c_se_conv(convs_acdc)
    [z_dc, var_vdc] = create_z_x_dc_se(graph_dc, dfDMEAS, ind_i_dc)
    # create losses constraints

    H = np.zeros((len(z_ac) + len(z_conv) + len(z_dc) + len(c_conv), len(var_t) + len(var_v) + len(var_vdc)))

    n_t = len(var_t)
    n_v = len(var_v)
    n_vdc = len(var_vdc)

    dz = np.zeros(len(z_ac) + len(z_conv) + len(z_dc) + len(c_conv))

    W = create_W(z_ac + z_conv + z_dc + c_conv, mode=2, prec_virtual=prec_virtual,scale_virt=scale_virt)
    lstdx = []
    lstdz = []
    it = 0


    a = 1
    conv = 0
    Vinici(graph, flatStart=2, ind_i=ind_i)
    Vinici_se_dc(graph_dc)


    offset_jdc= n_t + n_v



    while it < itmax:
        offset=calc_dz_ac(z_ac, graph, dz, offset=0)
        offset=calc_dz_conv(z_conv, convs_acdc,graph,graph_dc,dz,offset)
        offset=calc_dz_conv(c_conv, convs_acdc,graph,graph_dc,dz,offset)
        offset=calc_dz_dc(z_dc, graph_dc, dz, offset=offset)

        offset=calc_H_EE_ac(z_ac, var_t, var_v, graph, H)
        offset=calc_H_se_conv(z_conv, var_t, var_v, var_vdc, convs_acdc, graph, graph_dc, H, offset=offset)
        
        _=calc_C_se_ac(c_conv,var_t,var_v,convs_acdc,graph,H,offset)
        _=calc_C_se_loss(c_conv,var_t,var_v,convs_acdc,graph,H,offset)
        
        offset=calc_C_se_dc(c_conv,var_vdc,graph_dc,convs_acdc,H,offseti=offset, offset_j=offset_jdc)
        calc_H_se_dc(z_dc, var_vdc, graph_dc, H, offseti=offset, offset_j=offset_jdc)


        grad = np.matmul(np.matmul(H.T, W), dz)

        try:
            dx = NormalEQ_QR(H, W, dz, printcond=printcond, printmat=printmat)
        except:
            conv = 0
            it = 30
            break

        Jxk = np.matmul(np.matmul(dz, W), dz)
        if it == 0:
            norminicial = liang.norm(grad) if liang.norm(grad) > 1e-10 else 1

        new_X(graph, var_t, var_v, a * dx)
        new_X_dc_se(graph_dc, var_vdc, a * dx, offset=n_v + n_t)

        it = it + 1
        if printgrad:
            print("{:e},{:e}".format(liang.norm(grad) / norminicial, liang.norm(a * dx)))

        gradredux = liang.norm(grad) / norminicial
        maxdx = liang.norm(a * dx)
        lstdx.append(maxdx)
        lstdz.append(gradredux)

        if maxdx > 1e5:
            conv = 0
            it = 30
            break
        if gradredux < tol2 and maxdx < tol:
            txt = "Conv in {:d} iterations".format(it)
            if printres:
                print(liang.norm(grad) / norminicial)
                print(txt)
                prt_state(graph)
                prt_state_dc(graph_dc)
            conv = 1
            break
    return conv, lstdx, lstdz




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
#%%


dfDMEAS=save_DMEAS_acdc(graph,bran, graph_dc, bran_dc, convs_acdc, sys)
# %%
include_conv_nodes_in_graph(graph,ind_i, bran, convs_acdc)

for item in convs_acdc:
    Ploss=item.Ploss_se(graph)
    Pconv=item.Pac_se(graph)
    Pdc=item.Pdc_se(graph_dc)



SE_WLS_acdc(graph, graph_dc, convs_acdc, dfDMEAS, ind_i, ind_i_dc, ind_id_conv,scale_virt=0.1)
# %%
