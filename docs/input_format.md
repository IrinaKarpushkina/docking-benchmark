# Input Data Format

## Protein Files

Place PDB files in `data/input/proteins/`:
- Format: PDB files (`.pdb`)
- Each file should contain a single protein structure
- File name will be used as protein identifier

Example:
```
data/input/proteins/
├── 1ere.pdb
├── 4wnv.pdb
└── protein_A.pdb
```

## Ligand Files

Place CSV files with SMILES in `data/input/ligands/`:

### CSV Format

The CSV file must contain a column with SMILES strings. The column can be named:
- `smiles`
- `SMILES`
- `Smiles`
- `canonical_smiles`
- `canonical_SMILES`
- `Canonical_Smiles`
- `canonicalsmiles` (without underscore)

Optionally, you can include a column with ligand identifiers:
- `ligand_id`
- `id`
- `ligand`
- `name`

If no ID column is provided, ligands will be automatically named as `ligand_0`, `ligand_1`, etc.

### Example CSV Files

**Simple format:**
```csv
smiles
CC(=O)O
CCO
CCN(CC)CC
```

**With ligand IDs:**
```csv
ligand_id,smiles
L001,CC(=O)O
L002,CCO
L003,CCN(CC)CC
```

**With canonical SMILES:**
```csv
ligand_id,canonical_smiles
L001,CC(=O)O
L002,CCO
L003,CCN(CC)CC
```

**Multiple CSV files:**
```
data/input/ligands/
├── dataset1.csv
├── dataset2.csv
└── test_ligands.csv
```

### Processing Pipeline

For each SMILES string, the pipeline will:

1. **Parse SMILES** using RDKit
2. **Generate 3D coordinates** using RDKit's embedding and MMFF optimization
3. **Convert to required format**:
   - For QVina/Vina/Gnina: SMILES → SDF → PDBQT
   - For Boltz-2: SMILES used directly in YAML files

### Supported SMILES Features

- Standard organic molecules
- Aromatic rings
- Stereochemistry (E/Z, R/S)
- Charged molecules
- Most common functional groups

### Limitations

- Very large molecules (>1000 atoms) may fail embedding
- Some unusual SMILES patterns may not parse correctly
- 3D coordinate generation may fail for some complex structures

