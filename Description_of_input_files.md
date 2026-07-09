DBAR -- File with the information of the system's buses

id,type,V,theta,Pg,Qg,Pd,Qd,Bs

id - identification  of the bus
type - type of the bus (0 = ref, 1 = PV, 2 - PQ) 
V - Voltage in p.u.
theta - angle in grad
Pg - Active Power Generation p.u.
Qg - Reactive Power Generation p.u.
Pd - Load Active Power p.u.
Qd - Load Reactive Power p.u.

------------------------------------------------------------------------------------------

DBRAN -- File with the information of the system's branches

id - identification of the branches
type - Tipe of branch (1 = line, 2 = Trafo)
from - from bus id 
to - to bus id
r - series resistence (pu)
x - series reactance (pu)
bsh - line shunt suceptance (pu)
tap - tap of transforme (Vfrom/Vto)

------------------------------------------------------------------------------------------

DTCSC -- File with the information of the system's TCSC

id - identification of the TCSC
from - from bus id 
to - to bus id
a - alpha of tscc 
xtscc_ini - initial value of TCSC reactance
Pfesp - Power flow in the TCSC

------------------------------------------------------------------------------------------

DSVC -- File with the information of the system's SVC

id - identification of the SVC
bus - Bus where it is connected
Rt - Resistence of the coupling transformer
Xt - Reactance of the coupling transformer
Bini- sucptance initialization value of the SVC
BMAX - sucptance max value of the SVC
BMIN -  sucptance min value of the SVC
aini - alpha initialization value of the SVC
amax - alpha initialization value of the SVC
amin - alpha initialization value of the SVC

---------------------------------------------------------------------------------------

DUPFC -- File with the information of the system's UPFC

id - identification of the UPFC
from - from bus id 
to - to bus id
Vse - initial value of the series source magnitude (p.u.)
t_se - iniitial value of the series source phase angle (deg)
Vsh - iniitial value of the series source magnitude (p.u.)
t_sh - iniitial value of the series source phase angle (deg)
Psp - set point of terminal "s-p" active power flow (p.u.)
Qsp - set point of terminal "s-p" reactive power flow (p.u.)
Vp- ser point of terminal "p" voltage (p.u.)
Rse - series transformer resistence (p.u.)
Xse - series transformer reactance (p.u.)
Rsh - shunt transformer resistence (p.u.)
Xsh - shunt transformer reactance (p.u.)
Vse_max - max value for Vse 
Vse_min - min value for Vse 
Vsh_max - max value for Vsh 
Vsh_min - min value for Vsh 
mode - 1 control voltage at bus "p"/ 0 does note control voltage at bus "p"


---------------------------------------------------------------------------------------


DMED -- File with the measurement about the measurements

type,from,to,zmed,prec

type: Type of measurement (see list below)
from: From bus or element
to: To bus or element
zmed: Measured value
prec: Measurement precision 

type - measurement type  ( AC Network measurements
                            0-Active Power Injection (p.u.),
                            1-Reactive Power Injection (p.u.),
                            2-Active Power flow (p.u.),
                            3-Reactive Power Flow (p.u.),
                            4-Voltage Magnitude (p.u.), 
                            5 - Voltage phase angle (rad)
                            6 - Current inj Re (p.u.), 
                            7 - Current inj Im (p.u.),
                            8 - Current flow Re (p.u.),
                            9 - Current flow Im (p.u.)   
                            
                          FACTS measurements  
                            10 - X TCSC (p.u.),
                            11 - B SVC (p.u.),
                            12 - Voltage Magnitude sh UPFC,
                            13 - Voltage angle p-sh UPFC,
                            14 - Voltage Magnitude se UPFC,
                            15 - Voltage angle p-se UPFC 
                          DC Network measurements

                            100 - DC Network Power Injection 
                            101 - DC Network Current Injection
                            102 - DC Network Power flow
                            103 - DC Network Current flow
                            104 - DC Network Bus Voltage

                          ACDC converter measurements
                            200 - ACDC Converter internal filter bus active injection (p.u.) - virtual measurment it is a null injection
                            201 - ACDC Converter internal filter bus reactive injection (p.u.) - virtual measurment it is a null injection
                            202 - ACDC Converter internal transformer active power flow (p.u.) "to" field gives the direction (0 from grid to conv, 1 from conv to grid)
                            203 - ACDC Converter internal transformer reactive power flow (p.u.) "to" field gives the direction (0 from grid to conv, 1 from conv to grid)
                            220 - ACDC Converter internal reactor active power flow (p.u.) "to" field gives the direction (0 from grid to conv, 1 from conv to  
                            230 - ACDC Converter internal reactor reactive power flow (p.u.) "to" field gives the direction (0 from grid to conv, 1 from conv to grid)
                            204 - ACDC Converter internal filter bus voltage magnitude (p.u.) 
                            205 - ACDC Converter internal filter bus voltage angle (rad)
                            240 - ACDC Converter AC bus voltage magnitude (p.u.)
                            250 - ACDC Converter AC bus voltage angle (rad)
                            206 - ACDC Converter internal filter bus Current injection Re (p.u.) - virtual measurements (a null injection) 
                            207 - ACDC Converter internal filter bus Current injection Im (p.u.) - virtual measurements (a null injection) 
                            208 - ACDC Converter internal transformer Current flow Re (p.u.) "to" field gives the direction (0 from grid to conv, 1 from conv to grid)
                            209 - ACDC Converter internal transformer Current flow Im (p.u.) "to" field gives the direction (0 from grid to conv, 1 from conv to grid)
                            280 - ACDC Converter internal reactor Current flow Re (p.u.) "to" field gives the direction (0 from grid to conv, 1 from conv to grid)
                            290 - ACDC Converter internal reactor Current flow Im (p.u.) "to" field gives the direction (0 from grid to conv, 1 from conv to grid)
                            244 - ACDC Converter voltage ratio M = Vac/Vdc
                            )

