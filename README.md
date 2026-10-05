# Power Systems State Estimation – Python Implementation

Python implementation of algorithms for **Power System State Estimation (PSSE)** developed primarily for research and numerical validation.

The repository includes state estimation formulations for conventional AC networks and networks containing **FACTS devices**, including:

- Weighted Least Squares (WLS);
- Gauss–Newton solution;
- Levenberg–Marquardt solution;
- Backtracking line search;
- SVC models;
- TCSC models;
- UPFC models;
- SCADA and PMU measurements;
- Bayesian state estimation formulations.

## Structure

The main source code is organized under `src/`:

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
│   ├── BadData.py
│   └── io.py
│
├── tmp/                   # Temporary/debugging outputs
├── requirements.txt
├── environment.yml
├── LICENSE
└── README.md
```

The repository also contains several test systems and input datasets used for validating the implemented state estimation methods.

The code is being progressively reorganized to improve the separation between:

- network models and equations;
- measurement and residual calculations;
- Jacobian calculations;
- numerical solvers;
- state-estimation algorithms;
- input/output utilities.

## Installation

Clone the repository:

```bash
git clone https://github.com/vitorhpmelo/PowerSystemStateEstimationPython.git
cd PowerSystemStateEstimationPython
```

### Using Conda

Create the environment from the provided file:

```bash
conda env create -f environment.yml
conda activate psse-python
```

Alternatively, the Python dependencies can be installed using:

```bash
pip install -r requirements.txt
```

## Status

This repository contains research code developed over several stages of different research projects.

It is currently undergoing refactoring and cleanup to provide a more modular and consistent structure while preserving the numerical behavior of the original implementations.

The repository is **not extensively maintained**, and some scripts, test cases, or legacy implementations may not follow the current project structure or may require additional adjustments to run.

A new and substantially revised version of the implementation is currently under development and is expected to be released soon.

The code is therefore provided primarily for **research, validation, and reproducibility purposes**, rather than as a production-ready software package.

## License

This project is distributed under the terms described in the [`LICENSE`](LICENSE) file.