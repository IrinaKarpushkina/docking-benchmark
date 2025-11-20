#!/bin/bash
# Setup environment script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Setting up docking benchmark environment..."

# Check if conda is available
if command -v conda &> /dev/null; then
    echo "Creating conda environment..."
    conda env create -f "$PROJECT_DIR/environment.yml"
    conda activate docking-benchmark
else
    echo "Conda not found, using pip..."
    pip install -r "$PROJECT_DIR/requirements.txt"
fi

# Install the package
echo "Installing docking-benchmark package..."
cd "$PROJECT_DIR"
pip install -e .

echo "Environment setup complete!"










