# Environment Configuration

The docking benchmark supports running different stages in different conda environments. This is useful when:
- Preprocessing requires Meeko/RDKit (one environment)
- Each docking method requires its own dependencies (separate environments)

## Configuration

### Default Config (`config/default_config.yaml`)

```yaml
environments:
  preprocessing: "meeko"  # Environment for file preparation
```

### Methods Config (`config/methods_config.yaml`)

```yaml
qvina:
  conda_env: ""  # Empty = use preprocessing env
vina:
  conda_env: ""  # Empty = use preprocessing env
boltz2:
  conda_env: "boltz-env"  # Specific environment for Boltz-2
```

## How It Works

1. **Preprocessing Stage**: Runs in `preprocessing` environment (typically "meeko")
   - Converts SMILES to SDF
   - Converts SDF to PDBQT
   - Creates YAML files for Boltz-2

2. **Docking Stage**: Each method runs in its specified environment
   - If `conda_env` is empty, uses preprocessing environment
   - If `conda_env` is specified, uses that environment
   - Uses `conda run -n <env_name>` to execute commands

## Setting Up Environments

### Preprocessing Environment (Meeko)

```bash
conda create -n meeko python=3.9
conda activate meeko
pip install meeko rdkit-pypi pandas pyyaml biopython
```

### Boltz-2 Environment

```bash
conda create -n boltz-env python=3.10
conda activate boltz-env
# Install Boltz-2 according to its documentation
```

### Method-Specific Environments

For methods that need special dependencies:

```bash
# Example: QVina environment
conda create -n qvina-env python=3.9
conda activate qvina-env
# Install QVina and dependencies
```

## Configuration in Scripts

### `scripts/run_benchmark.sh`

```bash
# Conda environments
PREPROCESSING_ENV="meeko"
QVINA_ENV=""  # Uses PREPROCESSING_ENV if empty
VINA_ENV=""
BOLTZ_ENV="boltz-env"
```

The script will:
1. Activate preprocessing environment
2. Run Python script
3. Python script uses `conda run` for method-specific commands

## Command Line Override

You can override environments via command line by editing the config files or using environment variables.

## Troubleshooting

### Environment Not Found

If an environment doesn't exist, the script will:
- Print a warning
- Continue with current environment
- May fail if required binaries are not available

### Check Environments

```bash
conda env list
```

### Verify Environment Has Required Tools

```bash
conda activate meeko
python -c "import meeko; import rdkit; print('OK')"
```










