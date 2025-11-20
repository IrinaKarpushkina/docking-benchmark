# Installation Guide

## Requirements

- Python 3.8 or higher
- Conda (recommended) or pip
- Docking method binaries (QVina, Vina, Boltz-2, etc.)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd docking-benchmark
```

### 2. Install Dependencies

#### Using Conda (Recommended)

```bash
conda env create -f environment.yml
conda activate docking-benchmark
pip install -e .
```

#### Using pip

```bash
pip install -r requirements.txt
pip install -e .
```

### 3. Install Docking Methods

You need to install the docking methods separately:

- **QVina**: Download from [GitHub](https://github.com/QVina/QVina)
- **AutoDock Vina**: Download from [GitHub](https://github.com/ccsb-scripps/AutoDock-Vina)
- **Boltz-2**: Install via pip: `pip install boltz2`
- Other methods: Follow their respective installation instructions

### 4. Validate Installation

```bash
bash scripts/validate_installations.sh
```

## Docker Installation

If you prefer using Docker:

```bash
docker build -t docking-benchmark .
docker run -it docking-benchmark
```

## Singularity Installation

For HPC clusters with Singularity:

```bash
singularity build docking-benchmark.sif Singularity.def
singularity shell docking-benchmark.sif
```










