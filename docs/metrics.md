# Metrics

## Available Metrics

### RMSD (Root Mean Square Deviation)
- **Ligand RMSD**: Deviation of predicted ligand pose from reference
- **Pocket RMSD**: Deviation of pocket residues
- **Protein RMSD**: Overall protein structure deviation

### Affinity
- **Binding Affinity**: Predicted binding energy (kcal/mol)
- **IC50**: Half-maximal inhibitory concentration (if available)
- **pIC50**: Negative log of IC50

### Clash Score
- **Clash Count**: Number of atom pairs too close together
- **Clash Score**: Normalized clash metric

### Timing
- **Execution Time**: Time taken for docking (seconds)
- **Memory Usage**: Peak memory consumption (if available)

## Metric Extraction

Metrics are automatically extracted from:
- Log files (for Vina/QVina)
- JSON files (for Boltz-2)
- Output structures (for RMSD calculation)

## Output Format

Metrics are saved as CSV files:
- `metrics_{method}.csv` - Per-method metrics
- `metrics_all.csv` - Combined metrics
- `method_comparison.csv` - Statistical comparison










