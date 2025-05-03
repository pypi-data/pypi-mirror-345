# automesh

[![book](https://img.shields.io/badge/automesh-Book-blue?logo=mdbook&logoColor=000000)](https://autotwin.github.io/automesh)
[![crates](https://img.shields.io/crates/v/automesh?logo=rust&logoColor=000000&label=Crates&color=32592f)](https://crates.io/crates/automesh)
[![docs](https://img.shields.io/badge/Docs-API-e57300?logo=docsdotrs&logoColor=000000)](https://docs.rs/automesh)
[![pypi](https://img.shields.io/pypi/v/automesh?logo=pypi&logoColor=FBE072&label=PyPI&color=4B8BBE)](https://pypi.org/project/automesh)
[![docs](https://img.shields.io/badge/Docs-API-8CA1AF?logo=readthedocs)](https://automesh.readthedocs.io)

Automatic mesh generation.

## Introduction

The current Autotwin workflow has the following broad steps:

1. Medical imaging
2. Segmentation
3. Mesh generation
4. Simulation
5. Injury risk assessment

As of 2024-06-24, the workflow has demonstrated *automation*, the ability to complete part of the workflow without human interaction, on over 100 patient medical image data sets for both the **segmentation** and **mesh generation** steps. The **simulation** and **injury risk** assessment steps, however, remain as future work.

Since inception of this project, the production of an open-source software work product has been a cornerstone philosophy and aspiration. One part of the mesh generation step currently uses a closed-source, proprietary software service, which presents three limitations: (1) the software is not open-source, so at-large collaboration is unavailable, (2) void must be included as part of the mesh,[^void-inclusion] and (3) research-specific mesh experiments (e.g., Taubin smoothing, dual-space adaptivity) cannot be easily performed.

[^void-inclusion]: Void inclusion can unnecessarily bloat the model. For example, one recent proof-of-concept [exercise](https://github.com/autotwin/mesh/blob/main/doc/npy_to_mesh_part_3.md) using the IXI012-HH-1211-T1 data set showed that for a high-fidelity mesh created from segmented data, the void accounted for 2,389,783 elements (55%) of the total mesh 4,329,925 elements, with skull, cerebral spinal fluid, and brain, accounting for the remaining portions, 240,895 elements (6%), 448,654 elements (10%), and 1,250,593 elements (29%), respectively.

Elimination of the unnecessary void mesh is a top priority toward enhancement of mesh quality.  Additional mesh enchancement topics include smoothing and adaptivity.

Enhanced mesh quality can improve solver convergence rates, decrease overhead (memory footprint), and provide better overall geometric fidelity to the underlying human anatomy.

## Project Tasks

### Task 1: Solver Automation

*  **Mesh output decks**.  Mesh outputs are solver inputs.  Mesh outputs must be automated to provide solver integration and automation for Sierra Solid Mechanics (SSM) in the Genesis/Exodus format, ABAQUS (.inp format), and Generic ASCII (e.g., .vtk), specific format to be determined.
*  **Solver input decks**.  Current solver runs have hard-coded and manual hand-tailored input decks.  This process must be rewritten and fully automated.

### Task 2: Injury-Risk Automation

* **Globalized measures**.  Current workflows (e.g., MPS, MPSR, 95th percentile cloud maps) will be rewritten to become standardized and flexible, enabling automation.
* **Localized measures**.  Current whole-brain visualization workflows will be formalized into repeatable and flexible software recipes, making manual “point-and-click” GUI steps unnecessary.

### Task 3: Open-Source Mesh Generation

* **Open-source**.  Reproduce Sculpt mesh generation functionality as an open-source software component.

### Task 4: Mesh Enhancements

* **Filtering**.  Process the mesh with high-frequency filtering (e.g., Taubin smoothing).
* **Adaptivity**.  Process the mesh to be adaptivity, refining in regions of interest and coarsening in regions where abundance of mesh resolution is unnecessary.

Reference: 2024-06-21-1218-EST-ONR-Statement-of-Work.pdf

## Specific next steps

A minimum working example (MWE) of the `letter F` model (see [https://github.com/autotwin/mesh/blob/main/doc/npy_to_mesh.md](https://github.com/autotwin/mesh/blob/main/doc/npy_to_mesh.md)) will be used as a unit test through the following specific next steps:

* Given:
  * Semantic segmentation
    * as a [`.npy`](https://github.com/autotwin/mesh/blob/main/tests/files/letter_f_fiducial.npy) file,
    * as a [`.spn`](https://github.com/autotwin/mesh/blob/main/tests/files/letter_f.spn) file,
  * Configuration recipe (as a [`.yml`](https://github.com/autotwin/mesh/blob/main/tests/files/letter_f_autotwin.yml) file)
* Create:
  * Rust command line application that outputs equivalent Sculpt outputs, without void as a mesh constituent, as
    * ABAQUS ascii mesh file (as a `.inp` file)
    * SSM-ready mesh file (as a `.e` file, Genesis/Exodus [NetCDF](https://www.unidata.ucar.edu/software/netcdf/) binary format)
    * ascii neutral mesh file (as a file type that is currently to be determined)
* Next steps:
  * Taubin smoothing (see [Taubin 1995](https://dl.acm.org/doi/pdf/10.1145/218380.218473) and [Chen 2010](https://link.springer.com/content/pdf/10.1007/s00707-009-0274-0.pdf))
  * Dualization

## Getting Started

### Configuration

Install the module either as a **client** or as a **developer**.  The client installation is recommended for users in an analyst role, who will to use the module in an analysis workflow.  Knowledge of the Python and Rust programming languages is not necessary.  The developer installation is recommended for users in the code development role, who will create or update functionality.  Knowledge of the Python and Rust programming languages is required.

#### Client Installation - work in progress 2024-07-05

Following is an example using the HPC:

```bash
module purge

# load Python 3.11 or later
module load aue/anaconda3/2023.09  # (Python 3.11) or similar per the 'module avail' command

# change to a working directory, e.g., scratch
cd scratch

# if there is an existing virtual environment activated, deactivate it
deactivate

# if there is an existing virtual environment .venv folder, delete it
rm -rf .venv

# create a virtual environment called .venv
python -m venv .venv

# active the virtual environment
source .venv/bin/activate       # for bash shell
source .venv/bin/activate.csh   # for c shell

# install, for example, the latest development version, a tagged version,
# or a specific branch:

# example option 1/3: latest
python -m pip install git+ssh://git@github.com:autotwin/automesh.git

# example option 2/3: version v0.1.2
python -m pip install git+ssh://git@github.com:autotwin/automesh.git@v0.1.2

# example option 3/3: branch called 'dev'
python -m pip install git+ssh://git@github.com:autotwin/automesh.git@v0.1.2@dev
```

#### Developer Installation

Update `pip` and `setuptools` with a modern version of Python (e.g., Python 3.11):

```bash
python3.11 -m pip install --upgrade pip setuptools
```

Use a virtual environment called `.venv`, created with the [venv Python module](https://docs.python.org/3/library/venv.html), to keep the installation isolated from other Python projects.  Create the `.venv` virtual environment:

```bash
cd ~/autotwin/automesh/
python3.11 -m venv .venv

source .venv/bin/activate       # for bash shell
source .venv/bin/activate.csh   # for c shell
source .venv/bin/activate.fish  # for fish shell
.\.venv\Scripts\activate        # for powershell
```

Install with the `-e` (equivalently, `--editable`) flag to create an [editable installation](https://setuptools.pypa.io/en/latest/userguide/development_mode.html):

```bash
# deprecated
~~pip install -e .[develop]~~
pip install --upgrade pip
pip install maturin
maturin develop --extras develop
```

#### Developer Installation - Revised

We are using Maturin, not Setuptools, as a build backend.

2024-07-05: Ask mrbuche about
https://www.maturin.rs/project_layout

```bash
maturin develop
maturin develop --release --extras dev
maturin develop --release --extras develop

pre-commit install
# pre-commit installed at .git/hooks/pre-commit

pre-commit run --all-files
```

## References

* [Logs](doc/logs.md)
