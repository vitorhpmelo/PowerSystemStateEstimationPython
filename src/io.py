import csv
import numpy as np
from pathlib import Path

from src.networkcalc import *


def save_measurement_facts_order(z, var_UPFC, filename="tmp/z_order.csv"):
    """
    Save the measurement ordering used in the estimator.

    Parameters
    ----------
    z : list
        List of measurement objects.
    var_UPFC : dict
        Dictionary containing UPFC auxiliary variables.
    filename : str or Path
        Output csv file.
    """
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with filename.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["index", "type", "from", "to"])

        index = 1

        for meas in z:
            writer.writerow([
                index,
                meas.type,
                meas.k + 1,
                meas.m + 1,
            ])
            index += 1

        for key in var_UPFC:
            bus_from, bus_to = key.split("-")
            writer.writerow([
                index,
                "c_UPFC",
                bus_from,
                bus_to,
            ])
            index += 1


def save_variable_facts_order(
    var_t,
    var_v,
    var_x,
    var_svc,
    var_UPFC,
    var_UPFC_vsh,
    filename="tmp/var_order.csv",
):
    """
    Save the ordering of the state variables.

    Parameters
    ----------
    var_t : dict
        Voltage angle variables.
    var_v : dict
        Voltage magnitude variables.
    var_x : dict
        TCSC variables.
    var_svc : dict
        SVC variables.
    var_UPFC : dict
        UPFC series variables.
    var_UPFC_vsh : dict
        UPFC shunt voltage variables.
    filename : str or Path
        Output csv file.
    """
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with filename.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["index", "type", "bus"])

        index = 1

        variable_groups = [
            ("theta", var_t),
            ("V", var_v),
            ("TCSC", var_x),
            ("SVC", var_svc),
            ("UPFC_tse", var_UPFC),
            ("UPFC_tsh", var_UPFC),
            ("UPFC_Vse", var_UPFC),
            ("UPFC_Vsh", var_UPFC_vsh),
        ]

        for var_type, variables in variable_groups:
            for key in variables:
                writer.writerow([index, var_type, key])
                index += 1



def save_matrix(matrix, filename, float_format="%.15e"):
    """
    Save a matrix or vector to a CSV file.

    Parameters
    ----------
    matrix : array-like
        Matrix or vector to save.
    filename : str or Path
        Output CSV file.
    float_format : str, optional
        Floating-point format used when writing the file.
    """
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with filename.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        for row in matrix:
            # Handle both matrices and vectors
            try:
                writer.writerow(
                    [
                        float_format % x if isinstance(x, (float, int)) else x
                        for x in row
                    ]
                )
            except TypeError:
                writer.writerow(
                    [float_format % row if isinstance(row, (float, int)) else row]
                )


def save_se_inner_matrices(
    graph,
    df_DMEAS,
    ind_i,
    filename="python_se",
    output_dir="tmp",
    flatstart=True,
    ofsset_tcsc = True
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # Create measurements and state variables
    # --------------------------------------------------

    z, var_t, var_v = create_z_x(
        graph,
        df_DMEAS,
        ind_i,
    )

    if flatstart:
        FACTSini(graph, useDFACTS=True)
        Vinici(graph,flatStart=2,dfDMEAS=df_DMEAS,ind_i=ind_i)

    var_x = create_x_TCSC(graph)
    var_svc = create_x_SVC(graph)
    var_UPFC, c_upfc = create_c_x_UPFC(graph)

    if ofsset_tcsc & flatstart:
        for key in var_x.keys():
            key=key.split("-")
            m=int(key[1])
            graph[m].V=graph[m].V+1e-1
            # graph[m].theta=graph[m].theta+1e-2

    # --------------------------------------------------
    # Number of variables
    # --------------------------------------------------

    n_teta = len(var_t)
    n_v = len(var_v)
    n_TCSC = len(var_x)
    n_SVC = len(var_svc)
    n_UPFC = len(var_UPFC)

    nvar = (
        n_teta
        + n_v
        + n_TCSC
        + n_SVC
        + 4 * n_UPFC
    )

    nz = len(z)

    # --------------------------------------------------
    # Allocate matrices
    # --------------------------------------------------

    Htrad = np.zeros(
        (nz, n_teta + n_v)
    )

    HTCSC = np.zeros(
        (nz, n_TCSC)
    )

    HSVC = np.zeros(
        (nz, n_SVC)
    )

    UPFC = np.zeros(
        (nz, 4 * n_UPFC)
    )

    C_UPFC = np.zeros(
        (len(c_upfc), nvar)
    )

    # --------------------------------------------------
    # Auxiliary vectors
    # --------------------------------------------------

    dz = np.zeros(nz)
    h = np.zeros(nz)

    # Create the W matrix
    W = create_W(
        z + list(c_upfc),
        mode=0,
        prec_virtual=0.001,
    )

    # --------------------------------------------------
    # Calculate measurements
    # --------------------------------------------------

    calc_dz(
        z,
        graph,
        dz,
    )

    calc_h(
        z,
        graph,
        h,
    )

    calc_hUPFC(
        graph,
        var_UPFC,
        c_upfc,
    )

    # --------------------------------------------------
    # Calculate Jacobian blocks
    # --------------------------------------------------

    calc_H_EE(
        z,
        var_t,
        var_v,
        graph,
        Htrad,
    )

    calc_H_EE_TCSC(
        z,
        var_x,
        graph,
        HTCSC,
    )

    calc_H_EE_SVC(
        z,
        var_svc,
        graph,
        HSVC,
    )

    calc_H_EE_UPFC(
        z,
        var_UPFC,
        graph,
        UPFC,
    )

    calc_C_EE_UPFC(
        var_t,
        var_v,
        var_x,
        var_svc,
        var_UPFC,
        graph,
        C_UPFC,
    )

    # --------------------------------------------------
    # Assemble matrices
    # --------------------------------------------------

    Hx = np.concatenate(
        (
            Htrad,
            HTCSC,
            HSVC,
            UPFC,
        ),
        axis=1,
    )

    H = np.concatenate(
        (
            Hx,
            C_UPFC,
        ),
        axis=0,
    )
    h_all = np.concatenate(
        (
            h,
            c_upfc,
        ),
        axis=0,
    )
    # --------------------------------------------------
    # Save matrices
    # --------------------------------------------------

    np.savetxt(
        output_dir / "{name}_H.csv".format(name=filename),
        H,
        delimiter=",",
    )
    np.savetxt(
        output_dir / "{name}_h.csv".format(name=filename),
            h_all,
        delimiter=",",  
    )
    save_measurement_facts_order(
        z,
        var_UPFC,
        filename=output_dir / "{name}_z_order.csv".format(name=filename)  ,
    )

    save_variable_facts_order(
        var_t,
        var_v,
        var_x,
        var_svc,
        var_UPFC,
        var_UPFC,
        filename=output_dir / "{name}_x_order.csv".format(name=filename),
    )
    prt_state(graph)
    prt_state_FACTS(graph,var_x,var_svc,var_UPFC)
    return H