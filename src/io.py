import csv
from pathlib import Path

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