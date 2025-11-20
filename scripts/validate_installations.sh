#!/bin/bash
# Validate installations of docking methods

echo "Validating docking method installations..."

# Check QVina
if command -v qvina02 &> /dev/null; then
    echo "✓ QVina found: $(which qvina02)"
else
    echo "✗ QVina not found"
fi

# Check Vina
if command -v vina &> /dev/null; then
    echo "✓ AutoDock Vina found: $(which vina)"
else
    echo "✗ AutoDock Vina not found"
fi

# Check Boltz
if command -v boltz &> /dev/null; then
    echo "✓ Boltz-2 found: $(which boltz)"
else
    echo "✗ Boltz-2 not found"
fi

# Check Python dependencies
echo ""
echo "Checking Python dependencies..."
python3 -c "import rdkit; print('✓ RDKit')" 2>/dev/null || echo "✗ RDKit not found"
python3 -c "import meeko; print('✓ Meeko')" 2>/dev/null || echo "✗ Meeko not found"
python3 -c "import Bio; print('✓ BioPython')" 2>/dev/null || echo "✗ BioPython not found"
python3 -c "import yaml; print('✓ PyYAML')" 2>/dev/null || echo "✗ PyYAML not found"

echo ""
echo "Validation complete!"










