# Power Systems State Estimation – Python Implementation

Python implementation of algorithms for **Power System State Estimation (PSSE)** developed for research purposes.

The repository includes state estimation formulations for conventional AC networks and networks containing **FACTS devices**, including:

- Weighted Least Squares (WLS);
- Gauss–Newton solution;
- Levenberg–Marquardt solution;
- Backtracking line search;
- SVC models;
- TCSC models;
- UPFC models;
- SCADA and PMU measurements.

This repository is maintained primarily as a **research and validation implementation** and is also used for numerical comparison with the [`PowerSystemsStateEstimation.jl`](https://github.com/) Julia implementation.

## Structure

```text
.
├── src/
│   ├── SE.py
│   ├── SE_Bayesian.py
│   ├── networkcalc.py
│   ├── networkcalc_dc.py
│   ├── networkstruc.py
│   ├── readfiles.py
│   ├── classes.py
│   ├── meas_sampl.py
│   └── BadData.py
│
├── tmp/               # Temporary/debugging outputs
└── README.md
```

The code is currently being refactored to separate:

- network models and equations;
- residual calculations;
- Jacobian calculations;
- numerical solvers;
- state-estimation algorithms;
- input/output utilities.

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git
cd REPOSITORY_NAME
```

Create a Python environment and install the required dependencies.

```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Status

This repository contains research code and is currently under active refactoring.

The main goal of the refactoring is to preserve the numerical behavior of the original implementation while providing a cleaner and more modular architecture.

## Related project

A Julia implementation of the state-estimation framework is being developed in **PowerSystemsStateEstimation.jl**.

## License

See `LICENSE` for licensing information.