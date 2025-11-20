"""Interformer docking implementation (stub)."""

from pathlib import Path
from typing import Dict, List, Optional

from .base import BaseDocker


class InterformerDocker(BaseDocker):
    """Interformer docking method (stub)."""
    
    def __init__(self, config: Dict, processed_dir: Path, output_dir: Path,
                 preprocessing_env: Optional[str] = None):
        super().__init__(config, processed_dir, output_dir, preprocessing_env)
    
    def preprocess(self, protein_dir: Path, ligand_dir: Path):
        """Preprocess files for Interformer."""
        print("  Interformer preprocessing: STUB - Not implemented yet")
    
    def dock_all(self, ligand_dir: Optional[Path] = None):
        """Run Interformer docking."""
        print("  Interformer docking: STUB - Not implemented yet")
    
    def extract_metrics(self) -> List[Dict]:
        """Extract metrics from Interformer results."""
        print("  Interformer metrics extraction: STUB - Not implemented yet")
        return []

