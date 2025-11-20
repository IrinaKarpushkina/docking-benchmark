"""Error logging utilities for docking failures."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class DockingErrorLogger:
    """Log docking errors to JSON file."""
    
    def __init__(self, output_dir: Path):
        """
        Initialize error logger.
        
        Args:
            output_dir: Directory to save error log file.
        """
        self.output_dir = output_dir
        self.error_log_file = output_dir / "docking_errors.json"
        self.errors: List[Dict] = []
    
    def log_error(
        self,
        protein: str,
        ligand_name: str,
        smiles: Optional[str] = None,
        error_type: str = "unknown",
        error_message: str = "",
        log_file_path: Optional[Path] = None
    ) -> None:
        """
        Log a docking error.
        
        Args:
            protein: Protein name.
            ligand_name: Ligand identifier.
            smiles: SMILES string of the ligand (optional).
            error_type: Type of error ('timeout', 'subprocess_error', 'parse_error', etc.).
            error_message: Error message or description.
            log_file_path: Path to log file if available for extracting error details.
        """
        error_entry = {
            "protein": protein,
            "ligand": ligand_name,
            "smiles": smiles,
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Try to extract additional error info from log file
        if log_file_path and log_file_path.exists():
            try:
                with open(log_file_path, 'r') as f:
                    log_content = f.read()
                    # Extract last few lines that might contain error info
                    log_lines = log_content.strip().split('\n')
                    if log_lines:
                        error_entry["log_snippet"] = '\n'.join(log_lines[-10:])  # Last 10 lines
            except Exception:
                pass
        
        self.errors.append(error_entry)
        print(f"    [ERROR] Logged error for {protein}/{ligand_name}: {error_type}")
    
    def save(self) -> Path:
        """
        Save errors to JSON file.
        
        Returns:
            Path to error log file.
        """
        # Load existing errors if file exists
        existing_errors = []
        if self.error_log_file.exists():
            try:
                with open(self.error_log_file, 'r') as f:
                    existing_errors = json.load(f)
            except (json.JSONDecodeError, IOError):
                existing_errors = []
        
        # Merge with new errors (avoid duplicates)
        all_errors = existing_errors.copy()
        existing_keys = {(e.get('protein'), e.get('ligand')) for e in all_errors}
        
        for error in self.errors:
            key = (error.get('protein'), error.get('ligand'))
            if key not in existing_keys:
                all_errors.append(error)
                existing_keys.add(key)
        
        # Save to file
        self.error_log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.error_log_file, 'w') as f:
            json.dump(all_errors, f, indent=2)
        
        return self.error_log_file
    
    def get_ligand_smiles(self, ligand_name: str, ligand_dir: Path) -> Optional[str]:
        """
        Try to find SMILES for a ligand from CSV files.
        
        Args:
            ligand_name: Ligand identifier.
            ligand_dir: Directory containing CSV files with ligands.
        
        Returns:
            SMILES string if found, None otherwise.
        """
        import pandas as pd
        from ..preprocessing.ligand_prep import LigandPreparator
        
        # Try to find ligand in CSV files
        for csv_file in ligand_dir.glob("*.csv"):
            try:
                preparator = LigandPreparator(self.output_dir.parent / "processed")
                ligands_df = preparator.load_ligands_from_csv(csv_file)
                
                # Find SMILES column
                smiles_col = None
                for col in ['smiles', 'SMILES', 'Smiles', 'canonical_smiles', 
                           'canonical_SMILES', 'Canonical_Smiles', 'canonicalsmiles']:
                    if col in ligands_df.columns:
                        smiles_col = col
                        break
                
                if not smiles_col:
                    continue
                
                # Try to match by ligand_id or index
                if 'ligand_id' in ligands_df.columns:
                    matches = ligands_df[ligands_df['ligand_id'] == ligand_name]
                    if not matches.empty:
                        return matches.iloc[0][smiles_col]
                
                # Try to match by index if ligand_name is numeric
                try:
                    idx = int(ligand_name.replace('ligand_', ''))
                    if idx < len(ligands_df):
                        return ligands_df.iloc[idx][smiles_col]
                except (ValueError, IndexError, KeyError):
                    pass
                
                # Try direct match if ligand_name appears in any column
                for col in ligands_df.columns:
                    if ligand_name in ligands_df[col].values:
                        idx = ligands_df[ligands_df[col] == ligand_name].index[0]
                        return ligands_df.iloc[idx][smiles_col]
            except Exception:
                continue
        
        return None

