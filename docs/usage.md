# Usage Guide

## Quick Start

1. Prepare your data:
   - Place PDB files in `data/input/proteins/`
   - Place CSV files with SMILES in `data/input/ligands/`
   
   CSV file format:
   ```csv
   ligand_id,smiles
   L001,CC(=O)O
   L002,CCO
   L003,CCN(CC)CC
   ```
   
   Required columns:
   - `smiles` (or `SMILES`, `Smiles`, `canonical_smiles`, etc.) - SMILES strings
   
   Optional columns:
   - `ligand_id` (or `id`, `ligand`, `name`) - ligand identifiers

2. Configure the benchmark:
   - Edit `config/default_config.yaml` or
   - Edit `scripts/run_benchmark.sh`

3. Run the benchmark:
   ```bash
   bash scripts/run_benchmark.sh
   ```

## Command Line Interface

### Run Benchmark

```bash
python -m docking_benchmark.cli.run_benchmark \
  --base-dir data \
  --protein-dir data/input/proteins \
  --ligand-dir data/input/ligands \
  --methods qvina vina boltz2 \
  --random-state 42
```

Note: The ligand directory should contain CSV files with SMILES. The script will automatically:
1. Read SMILES from CSV files
2. Convert SMILES to 3D structures (SDF) using RDKit
3. Convert SDF to PDBQT for Vina-based methods
4. Use SMILES directly for Boltz-2

### Analyze Results

```bash
python -m docking_benchmark.cli.analyze_results \
  --results-dir data/results \
  --output-dir data/results/reports
```

## Configuration Files

### Default Config (`config/default_config.yaml`)

Main configuration file specifying:
- Base directories
- Methods to run
- Random seed
- Parallelization settings

### Methods Config (`config/methods_config.yaml`)

Method-specific parameters:
- Binary paths
- Exhaustiveness
- Other method-specific options

### SLURM Config (`config/slurm_config.yaml`)

SLURM job submission parameters for cluster execution.

## Output Structure

```
data/
├── processed/          # Prepared files
│   ├── qvina/
│   ├── vina/
│   └── boltz2/
├── results/            # Docking results
│   ├── qvina/
│   ├── vina/
│   ├── boltz2/
│   ├── metrics/        # Extracted metrics
│   └── reports/        # Generated reports
```

## Parallelization

### SLURM

For cluster execution, use SLURM:

```bash
sbatch scripts/run_slurm.sh
```

### Multiprocessing

Set in config:
```yaml
parallelization:
  type: "multiprocessing"
  max_workers: 4
```

