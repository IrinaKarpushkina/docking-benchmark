#!/bin/bash
# Enable strict mode and ensure all child processes are terminated on exit
set -euo pipefail
trap 'exit' INT TERM
trap 'kill 0' EXIT
# SLURM submission script for docking benchmark

#SBATCH --job-name=docking_benchmark
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=40G
#SBATCH --partition=aichem
#SBATCH --gres=gpu:1
#SBATCH --qos=high_gpu
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err

# Load environment
source ~/.bashrc

# Activate preprocessing environment
eval "$(conda shell.bash hook)"
conda activate meeko || {
    echo "Warning: Could not activate conda environment meeko"
    echo "Continuing with current environment..."
}

# Get project directory
PROJECT_DIR="${DOCKING_BENCHMARK_DIR:-/mnt/tank/scratch/okonovalova/docking-benchmark}"

# Install package in development mode (if not already installed)
cd "$PROJECT_DIR"
pip install -e . --quiet || {
    echo "Warning: Could not install package, trying with PYTHONPATH..."
    export PYTHONPATH="$PROJECT_DIR/src:$PYTHONPATH"
}

# Optional overrides (set before submitting the job)
PROTEIN_SETTINGS_FILE="${PROTEIN_SETTINGS_FILE:-}"
BOX_SETTINGS_FILE="${BOX_SETTINGS_FILE:-}"

# Precompute receptor PDBQT files prior to docking
# NOTE: Commented out for Boltz-2 as it works with protein sequences, not PDBQT files.
# Protein preparation is handled within each docking method's preprocess() method.
# Uncomment this block if you need to prepare proteins for QVina/Vina methods.
#
# python -u - <<'PY'
# from pathlib import Path
#
# from docking_benchmark.config import load_config
# from docking_benchmark.preprocessing import ProteinPreparator
# from docking_benchmark.utils import load_protein_settings
#
# project_dir = Path("${PROJECT_DIR}")
# protein_settings_env = "${PROTEIN_SETTINGS_FILE}"
#
# config = load_config()
#
# base_dir = Path(config['base_dir'])
# if not base_dir.is_absolute():
#     base_dir = project_dir / base_dir
#
# processed_dir = base_dir / config.get('processed_dir', 'processed')
# processed_dir.mkdir(parents=True, exist_ok=True)
#
# protein_dir = Path(config['protein_dir'])
# if not protein_dir.is_absolute():
#     protein_dir = project_dir / protein_dir
#
# settings_path = Path(protein_settings_env) if protein_settings_env else None
# protein_settings = load_protein_settings(settings_path)
# labox_config = config.get('labox', {})
#
# preparator = ProteinPreparator(processed_dir, settings=protein_settings, labox_config=labox_config)
#
# for pdb_file in sorted(protein_dir.glob('*.pdb')):
#     try:
#         preparator.prepare(pdb_file, method='qvina')
#     except Exception as exc:
#         raise SystemExit(f"Failed to prepare {pdb_file.name}: {exc}")
#
# preparator.export_preparation_manifest()
# PY


# Run benchmark (inherits optional overrides)
PROTEIN_SETTINGS_FILE="$PROTEIN_SETTINGS_FILE" BOX_SETTINGS_FILE="$BOX_SETTINGS_FILE" \
    bash "$PROJECT_DIR/scripts/run_benchmark.sh"

# Ensure the SLURM step exits cleanly
exit 0
