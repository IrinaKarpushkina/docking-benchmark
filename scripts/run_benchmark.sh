#!/bin/bash
# Docking Benchmark Runner Script
# This script configures and runs the docking benchmark pipeline

set -euo pipefail  # Exit on error, unset vars are errors, fail on pipeline errors
trap 'exit' INT TERM
trap 'kill 0' EXIT

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ============================================================================
# CONFIGURATION
# ============================================================================

# Base directories
BASE_DIR="${PROJECT_DIR}/data"
PROTEIN_DIR="${PROJECT_DIR}/data/input/proteins"
# LIGAND_DIR should contain CSV files with SMILES (see docs/input_format.md)
LIGAND_DIR="${PROJECT_DIR}/data/input/ligands"

# Optional override files (set via environment before running)
PROTEIN_SETTINGS_FILE="${PROTEIN_SETTINGS_FILE:-}"
BOX_SETTINGS_FILE="${BOX_SETTINGS_FILE:-}"

# Random state for reproducibility
RANDOM_STATE=42

# Conda environments
# Preprocessing environment (for Meeko, RDKit)
PREPROCESSING_ENV="meeko"
# Method-specific environments (leave empty to use preprocessing env)
QVINA_ENV="docking"  # If empty, uses PREPROCESSING_ENV
BOLTZ_ENV="boltz-env"  # Boltz-2 typically needs its own environment

# Methods to run (select from: qvina, boltz2, dynamicbind, unimol, interformer, gnina, plapt)
METHODS=("qvina" "boltz2_aut" "boltz2_cif")

# ============================================================================
# METHOD-SPECIFIC CONFIGURATIONS
# ============================================================================

# QVina configuration
QVINA_BINARY="qvina02"  # Update with your QVina binary path
QVINA_EXHAUSTIVENESS=8

# Boltz-2 configuration
BOLTZ_USE_MSA_SERVER=true  # Use MSA server for automatic MSA generation
BOLTZ_USE_POTENTIALS=true  # Use inference-time potentials

# ============================================================================
# RUN BENCHMARK
# ============================================================================

echo "=========================================="
echo "DOCKING BENCHMARK RUNNER"
echo "=========================================="
echo "Base directory: $BASE_DIR"
echo "Protein directory: $PROTEIN_DIR"
echo "Ligand directory: $LIGAND_DIR"
echo "Random state: $RANDOM_STATE"
echo "Methods: ${METHODS[*]}"
echo "=========================================="

# Activate preprocessing environment for running the script
# The script will handle method-specific environments internally
if [ -n "$PREPROCESSING_ENV" ]; then
    echo "Activating preprocessing environment: $PREPROCESSING_ENV"
    eval "$(conda shell.bash hook)"
    conda activate "$PREPROCESSING_ENV" || {
        echo "Warning: Could not activate conda environment $PREPROCESSING_ENV"
        echo "Continuing with current environment..."
    }
fi

# Build command
CMD="python3 -m docking_benchmark.cli.run_benchmark"
CMD="$CMD --base-dir $BASE_DIR"
CMD="$CMD --protein-dir $PROTEIN_DIR"
CMD="$CMD --ligand-dir $LIGAND_DIR"
CMD="$CMD --random-state $RANDOM_STATE"
CMD="$CMD --methods ${METHODS[*]}"

if [ -n "$PROTEIN_SETTINGS_FILE" ]; then
    CMD="$CMD --protein-settings $PROTEIN_SETTINGS_FILE"
fi

if [ -n "$BOX_SETTINGS_FILE" ]; then
    CMD="$CMD --box-settings $BOX_SETTINGS_FILE"
fi

# Add method-specific arguments
CMD="$CMD --qvina-binary $QVINA_BINARY"
CMD="$CMD --qvina-exhaustiveness $QVINA_EXHAUSTIVENESS"

if [ "$BOLTZ_USE_MSA_SERVER" = true ]; then
    CMD="$CMD --boltz-use-msa-server"
else
    CMD="$CMD --boltz-no-msa-server"
fi

if [ "$BOLTZ_USE_POTENTIALS" = true ]; then
    CMD="$CMD --boltz-use-potentials"
else
    CMD="$CMD --boltz-no-potentials"
fi

# Execute command
echo ""
echo "Running command:"
echo "$CMD"
echo ""
cd "$PROJECT_DIR"
eval $CMD
status=$?

echo ""
echo "=========================================="
echo "BENCHMARK COMPLETE"
echo "=========================================="
echo "Results saved to: $BASE_DIR/results/"
echo "Metrics saved to: $BASE_DIR/results/metrics/"
echo "=========================================="

exit $status
