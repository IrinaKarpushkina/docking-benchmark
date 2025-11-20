"""QVina docking implementation."""

import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

from .base import BaseDocker
from ..preprocessing import ProteinPreparator, LigandPreparator, BoxPreparator
from ..utils.env_utils import run_in_env
from ..utils import load_interaction_config, get_protein_ligand_pairs, get_proteins_for_ligand
from ..utils.error_logger import DockingErrorLogger


class QVinaDocker(BaseDocker):
    """QVina docking method."""
    
    def __init__(self, config: Dict, processed_dir: Path, output_dir: Path,
                 preprocessing_env: Optional[str] = None):
        super().__init__(config, processed_dir, output_dir, preprocessing_env)
        self.binary = config.get('binary', 'qvina02')
        self.exhaustiveness = config.get('exhaustiveness', 8)
        self.docking_timeout = config.get('docking_timeout', None)  # Timeout in seconds, None = no timeout
        
        self.method_dir = processed_dir / "qvina"
        self.results_dir = output_dir / "qvina"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        labox_config = config.get('labox', {})
        prep_settings = config.get('protein_settings', {})
        box_settings = config.get('box_settings', {})

        # Use shared directories for proteins and boxes
        self.protein_prep = ProteinPreparator(
            processed_dir,
            settings=prep_settings,
            labox_config=labox_config,
        )
        self.ligand_prep = LigandPreparator(self.method_dir)
        self.box_prep = BoxPreparator(
            processed_dir,
            settings=box_settings,
            labox_config=labox_config,
        )
    
    def preprocess(self, protein_dir: Path, ligand_dir: Path):
        """Preprocess files for QVina."""
        print("  Preparing files for QVina...")
        
        # Load interaction configuration
        interaction_config = load_interaction_config()
        pairs = get_protein_ligand_pairs(interaction_config)
        
        if not pairs:
            print("  Warning: No protein-ligand pairs found in interaction config. Skipping preprocessing.")
            return
        
        # Get unique proteins and ligands from config
        config_proteins = {pair[0] for pair in pairs}
        config_ligands = {pair[1] for pair in pairs}
        
        # Normalize config proteins for case-insensitive comparison
        normalized_config_proteins = {p.lower() for p in config_proteins}
        
        # Step 1: Prepare boxes first (using original PDB files)
        print("  Step 1: Calculating docking boxes...")
        for pdb_file in protein_dir.glob("*.pdb"):
            protein_name = pdb_file.stem
            normalized_name = protein_name.lower()
            if normalized_name in normalized_config_proteins:
                print(f"    Calculating box for protein: {protein_name}")
                self.box_prep.prepare(pdb_file, method='labox')
        
        # Step 2: Prepare proteins (only those in config)
        print("  Step 2: Preparing proteins...")
        for pdb_file in protein_dir.glob("*.pdb"):
            protein_name = pdb_file.stem
            normalized_name = protein_name.lower()
            if normalized_name in normalized_config_proteins:
                print(f"    Preparing protein: {protein_name}")
                self.protein_prep.prepare(pdb_file, method='qvina')
            else:
                print(f"    Skipping protein {protein_name} (not in interaction config)")
        
        # Step 3: Prepare ligands from CSV files (only those in config)
        print("  Step 3: Preparing ligands...")
        for csv_file in ligand_dir.glob("*.csv"):
            ligand_dataset = csv_file.stem
            if ligand_dataset not in config_ligands:
                print(f"    Skipping ligand dataset {ligand_dataset} (not in interaction config)")
                continue
            
            print(f"    Processing ligands from {csv_file.name}...")
            ligands_df = self.ligand_prep.load_ligands_from_csv(csv_file)
            
            # Get proteins associated with this ligand dataset
            associated_proteins = get_proteins_for_ligand(ligand_dataset, interaction_config)
            
            for _, row in ligands_df.iterrows():
                smiles = row['smiles']
                ligand_id = row['ligand_id']
                
                # Prepare ligand for each associated protein
                for protein_name in associated_proteins:
                    self.ligand_prep.prepare_from_smiles(
                        smiles, ligand_id, method='qvina', protein_name=protein_name
                    )
    
    def dock_all(self, ligand_dir: Optional[Path] = None):
        """Run QVina docking for all pairs."""
        print("  Running QVina docking...")
        
        # Initialize error logger
        error_logger = DockingErrorLogger(self.output_dir)
        
        # Load interaction configuration
        interaction_config = load_interaction_config()
        pairs = get_protein_ligand_pairs(interaction_config)
        
        print(f"  Found {len(pairs)} protein-ligand pairs in interaction config")
        
        if not pairs:
            print("  Warning: No protein-ligand pairs found in interaction config. Skipping docking.")
            return
        
        # Use shared directories for proteins and boxes
        protein_pdbqt_dir = self.processed_dir / "proteins"
        box_dir = self.processed_dir / "boxes"
        
        docked_count = 0
        for protein_name, ligand_dataset, ref_ligand, safe_chain in pairs:
            print(f"  Processing pair: protein={protein_name}, ligand_dataset={ligand_dataset}")
            # Find protein PDBQT file (case-insensitive)
            normalized_protein_name = protein_name.lower()
            protein_pdbqt = None
            
            # Try exact match first
            candidate = protein_pdbqt_dir / f"{protein_name}.pdbqt"
            if candidate.exists():
                protein_pdbqt = candidate
            else:
                # Try case-insensitive match
                for pdbqt_file in protein_pdbqt_dir.glob("*.pdbqt"):
                    if pdbqt_file.stem.lower() == normalized_protein_name:
                        protein_pdbqt = pdbqt_file
                        break
            
            if protein_pdbqt is None or not protein_pdbqt.exists():
                print(f"    Warning: Protein {protein_name} not found, skipping")
                continue
            
            # Use normalized name for results directory
            protein_results_dir = self.results_dir / normalized_protein_name
            protein_results_dir.mkdir(exist_ok=True)
            
            # Load box info (case-insensitive lookup)
            box_file = box_dir / f"{protein_name}.json"
            normalized_box_file = box_dir / f"{normalized_protein_name}.json"
            
            box_info = None
            if box_file.exists():
                import json
                with open(box_file) as f:
                    box_info = json.load(f)
            elif normalized_box_file.exists():
                import json
                with open(normalized_box_file) as f:
                    box_info = json.load(f)
            
            if box_info is None:
                box_info = {'center': [0, 0, 0], 'size': [20, 20, 20]}
            
            center = box_info['center']
            size = box_info['size']
            
            # Get ligands for this protein (from protein-specific directory, case-insensitive)
            ligand_pdbqt_dir = None
            # Try exact match first
            candidate_dir = self.ligand_prep.pdbqt_dir / protein_name
            if candidate_dir.exists() and candidate_dir.is_dir():
                ligand_pdbqt_dir = candidate_dir
            else:
                # Try case-insensitive match
                if self.ligand_prep.pdbqt_dir.exists():
                    for subdir in self.ligand_prep.pdbqt_dir.iterdir():
                        if subdir.is_dir() and subdir.name.lower() == normalized_protein_name:
                            ligand_pdbqt_dir = subdir
                            break
            
            if ligand_pdbqt_dir is None or not ligand_pdbqt_dir.exists():
                print(f"    Warning: No ligands found for protein {protein_name} (searched in {self.ligand_prep.pdbqt_dir}), skipping")
                continue
            
            for ligand_pdbqt in ligand_pdbqt_dir.glob("*.pdbqt"):
                ligand_name = ligand_pdbqt.stem
                output_pdbqt = protein_results_dir / f"{ligand_name}_out.pdbqt"
                log_file = protein_results_dir / f"{ligand_name}.log"
                
                if output_pdbqt.exists():
                    continue
                
                cmd = [
                    self.binary,
                    '--receptor', str(protein_pdbqt),
                    '--ligand', str(ligand_pdbqt),
                    '--center_x', str(center[0]),
                    '--center_y', str(center[1]),
                    '--center_z', str(center[2]),
                    '--size_x', str(size[0]),
                    '--size_y', str(size[1]),
                    '--size_z', str(size[2]),
                    '--out', str(output_pdbqt),
                    '--log', str(log_file),
                    '--exhaustiveness', str(self.exhaustiveness),
                ]
                
                try:
                    # Run in docking environment with timeout
                    start_time = time.time()
                    run_in_env(
                        cmd, 
                        env_name=self.docking_env, 
                        check=True, 
                        capture_output=True,
                        timeout=self.docking_timeout
                    )
                    elapsed_time = time.time() - start_time
                    docked_count += 1
                    print(f"    Docked: {normalized_protein_name}/{ligand_name} (took {elapsed_time:.1f}s)")
                except subprocess.TimeoutExpired as e:
                    # Timeout error
                    error_msg = f"Docking exceeded timeout of {self.docking_timeout}s"
                    smiles = None
                    if ligand_dir:
                        smiles = error_logger.get_ligand_smiles(ligand_name, ligand_dir)
                    error_logger.log_error(
                        protein=normalized_protein_name,
                        ligand_name=ligand_name,
                        smiles=smiles,
                        error_type="timeout",
                        error_message=error_msg,
                        log_file_path=log_file
                    )
                    print(f"    Timeout docking {normalized_protein_name}/{ligand_name} (>{self.docking_timeout}s)")
                except subprocess.CalledProcessError as e:
                    # Other subprocess errors
                    error_msg = str(e)
                    if hasattr(e, 'stderr') and e.stderr:
                        error_msg = e.stderr
                    elif hasattr(e, 'stdout') and e.stdout:
                        error_msg = e.stdout
                    
                    # Try to extract error type from message
                    error_type = "subprocess_error"
                    if "Parse error" in error_msg or "Unknown or inappropriate tag" in error_msg:
                        error_type = "parse_error"
                    elif "No atoms" in error_msg:
                        error_type = "no_atoms"
                    
                    smiles = None
                    if ligand_dir:
                        smiles = error_logger.get_ligand_smiles(ligand_name, ligand_dir)
                    error_logger.log_error(
                        protein=normalized_protein_name,
                        ligand_name=ligand_name,
                        smiles=smiles,
                        error_type=error_type,
                        error_message=error_msg,
                        log_file_path=log_file
                    )
                    print(f"    Error docking {normalized_protein_name}/{ligand_name}: {error_msg[:100]}")
                except Exception as e:
                    # Other unexpected errors
                    error_msg = str(e)
                    smiles = None
                    if ligand_dir:
                        smiles = error_logger.get_ligand_smiles(ligand_name, ligand_dir)
                    error_logger.log_error(
                        protein=normalized_protein_name,
                        ligand_name=ligand_name,
                        smiles=smiles,
                        error_type="unknown_error",
                        error_message=error_msg,
                        log_file_path=log_file
                    )
                    print(f"    Unexpected error docking {normalized_protein_name}/{ligand_name}: {error_msg}")
        
        # Save error log
        if error_logger.errors:
            error_file = error_logger.save()
            print(f"  Logged {len(error_logger.errors)} docking errors to {error_file}")
        
        print(f"  QVina docking complete: {docked_count} dockings performed")
    
    def extract_metrics(self) -> List[Dict]:
        """Extract metrics from QVina results."""
        metrics = []
        
        for protein_dir in self.results_dir.iterdir():
            if not protein_dir.is_dir():
                continue
            
            # Use normalized name (results are stored with normalized names)
            protein_name = protein_dir.name.lower()
            for log_file in protein_dir.glob("*.log"):
                ligand_name = log_file.stem
                affinity = self._extract_affinity(log_file)
                
                output_pdbqt = protein_dir / f"{ligand_name}_out.pdbqt"
                
                metrics.append({
                    'method': 'qvina',
                    'protein': protein_name,
                    'ligand': ligand_name,
                    'affinity': affinity,
                    'output_file': str(output_pdbqt) if output_pdbqt.exists() else None,
                })
        
        return metrics
    
    def _extract_affinity(self, log_file: Path) -> Optional[float]:
        """Extract affinity from QVina log file for the pose with minimum RMSD l.b."""
        try:
            with open(log_file) as f:
                lines = f.readlines()
            
            # Find the header line that contains "rmsd l.b."
            header_found = False
            poses = []
            
            for line in lines:
                if 'rmsd l.b.' in line.lower():
                    header_found = True
                    continue
                
                if header_found:
                    # Stop parsing if we encounter a non-data line (doesn't start with digit)
                    stripped = line.strip()
                    if not stripped or not stripped[0].isdigit():
                        # If we've already found poses, stop parsing
                        if poses:
                            break
                        continue
                    
                    # Parse mode lines (format: "   1         -0.0      0.000      0.000")
                    parts = stripped.split()
                    if len(parts) >= 4:
                        try:
                            mode = int(parts[0])
                            affinity = float(parts[1])
                            rmsd_lb = float(parts[2])
                            poses.append({
                                'mode': mode,
                                'affinity': affinity,
                                'rmsd_lb': rmsd_lb
                            })
                        except (ValueError, IndexError):
                            # Skip lines that don't match the expected format
                            continue
            
            if not poses:
                return None
            
            # Find the pose with minimum RMSD l.b.
            best_pose = min(poses, key=lambda x: x['rmsd_lb'])
            return best_pose['affinity']
            
        except Exception:
            pass
        return None

