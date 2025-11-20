"""Uni-Mol docking implementation (stub)."""

from pathlib import Path
from typing import Dict, List, Optional

from .base import BaseDocker


class UniMolDocker(BaseDocker):
    """Uni-Mol docking method (stub)."""
    
    def __init__(self, config: Dict, processed_dir: Path, output_dir: Path,
                 preprocessing_env: Optional[str] = None):
        super().__init__(config, processed_dir, output_dir, preprocessing_env)
    
    def preprocess(self, protein_dir: Path, ligand_dir: Path):
        """Preprocess files for Uni-Mol."""
        print("  Uni-Mol preprocessing: STUB - Not implemented yet")
    
    def dock_all(self, ligand_dir: Optional[Path] = None):
        """Run Uni-Mol docking."""
        print("  Uni-Mol docking: STUB - Not implemented yet")
    
    def extract_metrics(self) -> List[Dict]:
        """Extract metrics from Uni-Mol results."""
        print("  Uni-Mol metrics extraction: STUB - Not implemented yet")
        return []

