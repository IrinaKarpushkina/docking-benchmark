# Changelog: SMILES Input Support

## Summary

Updated the docking benchmark to accept ligands in SMILES format from CSV files instead of SDF files.

## Changes

### 1. Ligand Preparation (`src/docking_benchmark/preprocessing/ligand_prep.py`)

**New Features:**
- `load_ligands_from_csv()` - Reads CSV files with SMILES
- `prepare_from_smiles()` - Converts SMILES to required formats
- `_smiles_to_sdf()` - Converts SMILES to 3D SDF using RDKit

**Process:**
- For QVina/Vina/Gnina: SMILES → SDF → PDBQT
- For Boltz-2: SMILES used directly in YAML files

**CSV Format:**
- Required column: `smiles` (or `SMILES`, `Smiles`)
- Optional column: `ligand_id` (or `id`, `ligand`, `name`)

### 2. Docking Modules

**Updated:**
- `docking/qvina.py` - Now reads CSV files instead of SDF
- `docking/vina.py` - Now reads CSV files instead of SDF
- `docking/boltz2.py` - Now reads CSV files instead of SDF

**Process:**
- Each module iterates through CSV files in ligand directory
- For each SMILES, converts to appropriate format
- Maintains ligand IDs from CSV or generates automatic IDs

### 3. Documentation

**Updated:**
- `README.md` - Updated quick start guide
- `docs/usage.md` - Added CSV format examples
- `docs/input_format.md` - New file with detailed input format specification

**New:**
- `docs/input_format.md` - Complete guide on input data formats

### 4. Scripts

**Updated:**
- `scripts/run_benchmark.sh` - Added comment about CSV format

## Migration Guide

### Old Format (SDF files)
```
data/input/ligands/
├── ligand1.sdf
├── ligand2.sdf
└── ligand3.sdf
```

### New Format (CSV files)
```
data/input/ligands/
├── dataset1.csv
└── dataset2.csv
```

**CSV Example:**
```csv
ligand_id,smiles
L001,CC(=O)O
L002,CCO
L003,CCN(CC)CC
```

## Technical Details

### SMILES to 3D Conversion

1. **Parse SMILES** using `RDKit.Chem.MolFromSmiles()`
2. **Add hydrogens** using `Chem.AddHs()`
3. **Generate 3D coordinates**:
   - `AllChem.EmbedMolecule()` - Embed with random seed for reproducibility
   - `AllChem.MMFFOptimizeMolecule()` - Optimize geometry
4. **Write SDF** using `Chem.SDWriter()`

### Error Handling

- Invalid SMILES are skipped with warning
- Failed 3D embedding attempts are logged
- Missing CSV columns raise clear error messages

## Benefits

1. **Easier input**: SMILES strings are easier to work with than SDF files
2. **Batch processing**: Multiple ligands in single CSV file
3. **Metadata support**: Can include additional columns (IDs, properties, etc.)
4. **Reproducibility**: Random seed ensures consistent 3D structures

## Backward Compatibility

**Not maintained**: The old SDF-based workflow is no longer supported. If you have SDF files, you can:
1. Convert SDF to SMILES using RDKit
2. Create CSV files with SMILES
3. Use the new workflow










