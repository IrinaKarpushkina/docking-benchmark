"""Ligand preparation module using Meeko and RDKit."""

import pandas as pd
import subprocess
from pathlib import Path
from typing import Optional, Dict, List
try:
    from meeko import MoleculePreparation, PDBQTWriterLegacy
    from rdkit import Chem
    from rdkit.Chem import AllChem
except ImportError:
    MoleculePreparation = None
    PDBQTWriterLegacy = None
    Chem = None
    AllChem = None


class LigandPreparator:
    """Prepare ligand structures for docking from SMILES in CSV files."""
    
    def __init__(self, output_dir: Path):
        """
        Initialize ligand preparator.
        
        Args:
            output_dir: Directory to save prepared ligands.
        """
        self.output_dir = output_dir
        # Determine the root processed directory (strip method-specific subdir if present)
        if output_dir.name in {"processed", "processed_dir"}:
            self.processed_root = output_dir
        else:
            self.processed_root = output_dir.parent
        
        self.pdbqt_dir = self.processed_root / "pdbqt"
        self.sdf_dir = self.processed_root / "sdf"
        self.pdbqt_dir.mkdir(parents=True, exist_ok=True)
        self.sdf_dir.mkdir(parents=True, exist_ok=True)
        
        # Backwards compatibility attribute (points to global PDBQT directory)
        self.ligand_dir = self.pdbqt_dir
    
    def load_ligands_from_csv(self, csv_path: Path) -> pd.DataFrame:
        """
        Load ligands from CSV file.
        
        Expected CSV format:
        - Must have a column with SMILES (can be named 'smiles', 'SMILES', 'Smiles', 
          'canonical_smiles', 'canonical_SMILES', etc.)
        - Optionally has 'ligand_id' or 'id' column for ligand identifiers
        
        Args:
            csv_path: Path to CSV file with SMILES.
        
        Returns:
            DataFrame with ligands.
        """
        # Try to read CSV with error handling
        # First, try to detect separator by reading first line
        with open(csv_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            # Count separators
            comma_count = first_line.count(',')
            semicolon_count = first_line.count(';')
            tab_count = first_line.count('\t')
            
            # Determine separator (prefer semicolon if it has more occurrences)
            if semicolon_count > 0 and semicolon_count >= comma_count:
                sep = ';'
            elif tab_count > comma_count:
                sep = '\t'
            else:
                sep = ','
        
        print(f"    Detected separator: '{sep}' (commas: {comma_count}, semicolons: {semicolon_count}, tabs: {tab_count})")
        
        # Try different separators in order of likelihood
        separators_to_try = [sep, ';', ',', '\t']
        df = None
        
        for current_sep in separators_to_try:
            try:
                # Try with pandas >= 1.3.0
                try:
                    df = pd.read_csv(csv_path, sep=current_sep, on_bad_lines='skip', engine='python', encoding='utf-8')
                except TypeError:
                    # Fallback for older pandas versions
                    df = pd.read_csv(csv_path, sep=current_sep, error_bad_lines=False, 
                                   warn_bad_lines=False, engine='python', encoding='utf-8')
                
                # Check if we got multiple columns (indicates correct separator)
                if len(df.columns) > 1:
                    print(f"    Successfully read CSV with separator '{current_sep}' ({len(df.columns)} columns)")
                    break
                else:
                    # Only one column - probably wrong separator
                    df = None
                    continue
            except Exception as e:
                print(f"    Warning: Error reading CSV with separator '{current_sep}': {e}")
                continue
        
        if df is None or df.empty:
            raise ValueError(f"CSV file {csv_path} could not be parsed with any separator")
        
        # Find SMILES column (check for smiles, canonical_smiles, or similar)
        smiles_col = None
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in ['smiles', 'smile', 'canonical_smiles', 'canonical_smile', 
                           'canonicalsmiles', 'canonicalsmile']:
                smiles_col = col
                break
        
        if smiles_col is None:
            raise ValueError(f"No SMILES column found in {csv_path}. Available columns: {list(df.columns)}")
        
        # Find ID column
        id_col = None
        for col in df.columns:
            if col.lower() in ['ligand_id', 'id', 'ligand', 'name']:
                id_col = col
                break
        
        # Create standardized dataframe
        result_df = pd.DataFrame()
        result_df['smiles'] = df[smiles_col].astype(str)
        if id_col:
            result_df['ligand_id'] = df[id_col].astype(str)
        else:
            result_df['ligand_id'] = [f"ligand_{i}" for i in range(len(df))]
        
        # Remove rows with invalid SMILES (empty, NaN, or "nan")
        result_df = result_df[result_df['smiles'].notna()]
        result_df = result_df[result_df['smiles'] != '']
        result_df = result_df[result_df['smiles'].str.lower() != 'nan']
        
        print(f"    Loaded {len(result_df)} ligands from {csv_path.name}")
        
        return result_df
    
    def prepare_from_smiles(self, smiles: str, ligand_id: str, method: str = "all", 
                           protein_name: Optional[str] = None) -> Dict[str, Path]:
        """
        Prepare ligand from SMILES string for a specific method.
        
        Args:
            smiles: SMILES string.
            ligand_id: Unique identifier for the ligand.
            method: Method name ('qvina', 'vina', 'boltz2', etc.)
            protein_name: Optional protein name to organize files in subdirectories.
        
        Returns:
            Dictionary mapping method names to prepared file paths or SMILES.
        """
        results = {}
        
        if method in ['qvina', 'vina', 'gnina']:
            # Organize files by protein if specified (use normalized name for consistency)
            if protein_name:
                normalized_protein_name = protein_name.lower()
                protein_sdf_dir = self.sdf_dir / normalized_protein_name
                protein_pdbqt_dir = self.pdbqt_dir / normalized_protein_name
                protein_sdf_dir.mkdir(parents=True, exist_ok=True)
                protein_pdbqt_dir.mkdir(parents=True, exist_ok=True)
                sdf_path = protein_sdf_dir / f"{ligand_id}.sdf"
                pdbqt_path = protein_pdbqt_dir / f"{ligand_id}.pdbqt"
            else:
                sdf_path = self.sdf_dir / f"{ligand_id}.sdf"
                pdbqt_path = self.pdbqt_dir / f"{ligand_id}.pdbqt"
            
            sdf_missing = not sdf_path.exists() or sdf_path.stat().st_size == 0
            pdbqt_missing = not pdbqt_path.exists() or pdbqt_path.stat().st_size == 0
            
            if sdf_missing:
                self._smiles_to_sdf(smiles, sdf_path)
            if pdbqt_missing:
                self._sdf_to_pdbqt(sdf_path, pdbqt_path)
            
            results[method] = pdbqt_path
        
        elif method == 'boltz2':
            # For Boltz-2, we just need SMILES
            results[method] = smiles
        
        return results
    
    def _smiles_to_sdf(self, smiles: str, sdf_path: Path):
        """
        Convert SMILES to SDF file.
        
        Uses RDKit if available, otherwise falls back to Open Babel.
        
        Args:
            smiles: SMILES string.
            sdf_path: Output SDF file path.
        """
        # Try RDKit first if available
        if Chem is not None and AllChem is not None:
            try:
                # Parse SMILES
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    raise RuntimeError(f"Failed to parse SMILES: {smiles}")
                
                # Add hydrogens
                mol = Chem.AddHs(mol)
                
                # Generate 3D coordinates
                AllChem.EmbedMolecule(mol, randomSeed=42)
                AllChem.MMFFOptimizeMolecule(mol)
                
                # Write to SDF
                writer = Chem.SDWriter(str(sdf_path))
                writer.write(mol)
                writer.close()
                print(f"    [PREPARATION] Ligand {sdf_path.stem}: SDF prepared using RDKit")
                print(f"    Converted SMILES to SDF using RDKit: {sdf_path.name}")
                return
            except Exception as e:
                print(f"    Warning: RDKit conversion failed: {e}, trying Open Babel...")
        
        # Fallback to Open Babel
        try:
            # Open Babel can convert SMILES to SDF directly
            # Format: obabel -:"SMILES" -O output.sdf --gen3d
            cmd = ['obabel', f'-:{smiles}', '-O', str(sdf_path), '--gen3d', '-h']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"    [PREPARATION] Ligand {sdf_path.stem}: SDF prepared using Open Babel (fallback)")
            print(f"    Converted SMILES to SDF using Open Babel: {sdf_path.name}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to convert SMILES to SDF with Open Babel: {e.stderr}")
        except FileNotFoundError:
            raise ImportError("Neither RDKit nor Open Babel (obabel) is available for SMILES to SDF conversion")
    
    def _sdf_to_pdbqt(self, sdf_path: Path, pdbqt_path: Path):
        """
        Convert SDF to PDBQT using Meeko.
        
        Args:
            sdf_path: Input SDF file.
            pdbqt_path: Output PDBQT file.
        """
        # Try RDKit + Meeko pipeline first if available
        if Chem is not None and MoleculePreparation is not None:
            try:
                mol = Chem.MolFromMolFile(str(sdf_path), removeHs=False)
                if mol is None:
                    raise RuntimeError(f"Failed to read molecule from {sdf_path}")

                mol = Chem.AddHs(mol)
                Chem.Kekulize(mol, clearAromaticFlags=True)

                prep = MoleculePreparation()
                setups = prep.prepare(mol)
                writer = PDBQTWriterLegacy()
                result = writer.write_string(setups[0])

                if isinstance(result, tuple):
                    pdbqt_str = result[0]
                else:
                    pdbqt_str = result

                with open(pdbqt_path, "w") as f:
                    f.write(pdbqt_str)

                print(f"    [PREPARATION] Ligand {pdbqt_path.stem}: PDBQT prepared using RDKit+Meeko")
                print(f"    Converted SDF to PDBQT using RDKit+Meeko: {pdbqt_path.name}")
                return
            except Exception as e:
                print(f"    Warning: RDKit+Meeko conversion failed for {sdf_path.name}: {e}. Trying Open Babel...")

        # Fallback to Open Babel
        try:
            cmd = ['obabel', str(sdf_path), '-O', str(pdbqt_path), '--gen3d', '-h']
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"    [PREPARATION] Ligand {pdbqt_path.stem}: PDBQT prepared using Open Babel (fallback)")
            print(f"    Converted SDF to PDBQT using Open Babel: {pdbqt_path.name}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to convert SDF to PDBQT with Open Babel: {e.stderr}")
        except FileNotFoundError:
            raise ImportError("Neither RDKit/Meeko nor Open Babel are available for SDF to PDBQT conversion")

