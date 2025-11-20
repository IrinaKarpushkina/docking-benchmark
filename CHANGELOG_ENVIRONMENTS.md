# Changelog: Multi-Environment Support

## Summary

Added support for running different stages of the docking pipeline in different conda environments.

## Changes

### 1. Configuration Files

**`config/default_config.yaml`:**
- Added `environments` section
- `preprocessing`: Environment for file preparation (Meeko, RDKit)

**`config/methods_config.yaml`:**
- Added `conda_env` parameter for each method
- If empty, uses preprocessing environment
- If specified, uses that environment for docking

### 2. Environment Utilities (`src/docking_benchmark/utils/env_utils.py`)

**New Functions:**
- `run_in_env()` - Run command in specified conda environment
- `check_env_exists()` - Check if conda environment exists
- `get_python_in_env()` - Get Python executable in environment
- `get_conda_env_command()` - Get command prefix for conda run

**Implementation:**
- Uses `conda run -n <env_name>` to execute commands
- Falls back gracefully if conda is not available

### 3. Base Docker Class (`src/docking_benchmark/docking/base.py`)

**Updated:**
- Added `preprocessing_env` parameter to `__init__()`
- Added `docking_env` property (from config or preprocessing_env)
- Added `run_command_in_env()` helper method

### 4. Docking Modules

**Updated all modules:**
- `qvina.py` - Uses `run_in_env()` for docking commands
- `vina.py` - Uses `run_in_env()` for docking commands
- `boltz2.py` - Uses `run_in_env()` for docking commands
- All stub modules updated with environment support

### 5. Main Module (`src/docking_benchmark/main.py`)

**Updated:**
- Reads `environments.preprocessing` from config
- Passes `preprocessing_env` to all docker instances
- Each docker uses its own `conda_env` or falls back to preprocessing

### 6. Scripts

**`scripts/run_benchmark.sh`:**
- Added environment configuration variables
- Activates preprocessing environment before running
- Python script handles method-specific environments internally

### 7. Documentation

**New:**
- `docs/environments.md` - Complete guide on environment configuration

## Usage

### Configuration

**Option 1: YAML files**
```yaml
# config/default_config.yaml
environments:
  preprocessing: "meeko"

# config/methods_config.yaml
boltz2:
  conda_env: "boltz-env"
```

**Option 2: Script variables**
```bash
# scripts/run_benchmark.sh
PREPROCESSING_ENV="meeko"
BOLTZ_ENV="boltz-env"
```

### How It Works

1. **Preprocessing**: Runs in `preprocessing` environment
   - SMILES → SDF conversion (RDKit)
   - SDF → PDBQT conversion (Meeko)
   - YAML file creation (Python)

2. **Docking**: Each method runs in its specified environment
   - QVina/Vina: Uses preprocessing env (if not specified)
   - Boltz-2: Uses `boltz-env` (from config)
   - Commands executed via `conda run -n <env>`

### Example Setup

```bash
# Create preprocessing environment
conda create -n meeko python=3.9
conda activate meeko
pip install meeko rdkit-pypi pandas pyyaml biopython

# Create Boltz-2 environment
conda create -n boltz-env python=3.10
conda activate boltz-env
# Install Boltz-2 according to documentation
```

## Benefits

1. **Isolation**: Each method can have its own dependencies
2. **Flexibility**: Easy to switch between different environment setups
3. **Compatibility**: Avoids dependency conflicts between methods
4. **Reproducibility**: Clear environment specification in config

## Backward Compatibility

- If no environments are specified, runs in current environment
- If conda is not available, falls back to direct command execution
- Existing workflows continue to work without changes










