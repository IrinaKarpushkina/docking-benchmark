"""Clash score calculation module.

This implementation is based on the methodology described in:
CompassDock: Comprehensive Accurate Assessment Approach for Deep Learning-Based 
Molecular Docking in Inference and Fine-Tuning
arXiv:2406.06841
https://arxiv.org/abs/2406.06841

The clash score counts the number of atom pairs between ligand and protein
that are closer than a threshold distance, indicating steric clashes.
"""

from pathlib import Path
from typing import Optional, List, Tuple
import numpy as np

try:
    from Bio.PDB import PDBParser
    from Bio.PDB.PDBExceptions import PDBConstructionWarning
    import warnings
    warnings.simplefilter('ignore', PDBConstructionWarning)
except ImportError:
    PDBParser = None

try:
    from rdkit import Chem
except ImportError:
    Chem = None


def calculate_clash_score(
    structure_path: Path,
    protein_path: Optional[Path] = None,
    cutoff: float = 2.0
) -> Optional[float]:
    """
    Calculate clash score for a protein-ligand complex.
    
    The clash score is the number of atom pairs between ligand and protein
    that are closer than the cutoff distance, indicating steric clashes.
    
    Args:
        structure_path: Path to structure file containing ligand (PDB, PDBQT, SDF, CIF).
                       If protein_path is None, this should contain the full complex.
        protein_path: Optional path to protein structure file (PDB, PDBQT).
                      If provided, structure_path should contain only the ligand.
        cutoff: Distance cutoff for clash detection in Angstroms (default: 2.0).
                Pairs of atoms closer than this distance are considered clashes.
    
    Returns:
        Clash score (number of clashes), or None if calculation fails.
    
    References:
        CompassDock: Comprehensive Accurate Assessment Approach for Deep Learning-Based 
        Molecular Docking in Inference and Fine-Tuning
        arXiv:2406.06841
        https://arxiv.org/abs/2406.06841
    """
    try:
        # Extract ligand and protein coordinates
        if protein_path is not None:
            # Separate ligand and protein files
            ligand_coords = _extract_coordinates(structure_path, is_ligand=True)
            protein_coords = _extract_coordinates(protein_path, is_ligand=False)
        else:
            # Try to extract both from complex file
            # For PDBQT, we'll try to identify ligand vs protein by chain/residue
            ligand_coords, protein_coords = _extract_from_complex(structure_path)
        
        if ligand_coords is None or protein_coords is None:
            return None
        
        if len(ligand_coords) == 0 or len(protein_coords) == 0:
            return None
        
        # Calculate distances between all ligand and protein atoms
        ligand_coords = np.array(ligand_coords)
        protein_coords = np.array(protein_coords)
        
        # Use efficient distance calculation
        # Calculate pairwise distances using broadcasting
        distances = np.sqrt(((ligand_coords[:, np.newaxis, :] - protein_coords[np.newaxis, :, :]) ** 2).sum(axis=2))
        
        # Count pairs with distance < cutoff
        clash_count = np.sum(distances < cutoff)
        
        return int(clash_count)
    
    except Exception as e:
        # Return None on any error
        return None


def _extract_coordinates(file_path: Path, is_ligand: bool = True) -> Optional[List[Tuple[float, float, float]]]:
    """
    Extract atomic coordinates from a structure file.
    
    Args:
        file_path: Path to structure file.
        is_ligand: If True, extract ligand coordinates; if False, extract protein coordinates.
    
    Returns:
        List of (x, y, z) coordinate tuples, or None on error.
    """
    suffix = file_path.suffix.lower()
    coords = []
    
    if suffix in ['.pdb', '.pdbqt']:
        coords = _extract_from_pdb(file_path, is_ligand)
    elif suffix == '.sdf':
        coords = _extract_from_sdf(file_path)
    elif suffix == '.cif':
        coords = _extract_from_cif(file_path, is_ligand)
    else:
        # Try PDB format as fallback
        coords = _extract_from_pdb(file_path, is_ligand)
    
    return coords if coords else None


def _extract_from_pdb(file_path: Path, is_ligand: bool = True) -> List[Tuple[float, float, float]]:
    """Extract coordinates from PDB or PDBQT file."""
    coords = []
    
    if PDBParser is None:
        # Fallback: simple text parsing for PDBQT
        return _parse_pdbqt_simple(file_path, is_ligand)
    
    try:
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure('structure', str(file_path))
        
        for model in structure:
            for chain in model:
                for residue in chain:
                    # For PDBQT, ligands are typically HETATM records
                    # For protein, we want ATOM records
                    residue_name = residue.get_resname()
                    
                    # Simple heuristic: if is_ligand, get HETATM; otherwise get ATOM
                    # In PDBQT, ligands are usually HETATM
                    if is_ligand:
                        # Look for HETATM (ligands) or small residues
                        if residue.id[0] != ' ' or residue_name not in ['ALA', 'ARG', 'ASN', 'ASP', 'CYS',
                                                                        'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
                                                                        'LEU', 'LYS', 'MET', 'PHE', 'PRO',
                                                                        'SER', 'THR', 'TRP', 'TYR', 'VAL']:
                            for atom in residue:
                                coord = atom.get_coord()
                                coords.append((coord[0], coord[1], coord[2]))
                    else:
                        # Protein atoms: standard amino acids
                        if residue.id[0] == ' ' and residue_name in ['ALA', 'ARG', 'ASN', 'ASP', 'CYS',
                                                                     'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
                                                                     'LEU', 'LYS', 'MET', 'PHE', 'PRO',
                                                                     'SER', 'THR', 'TRP', 'TYR', 'VAL']:
                            for atom in residue:
                                coord = atom.get_coord()
                                coords.append((coord[0], coord[1], coord[2]))
    except Exception:
        # Fallback to simple parsing
        return _parse_pdbqt_simple(file_path, is_ligand)
    
    return coords


def _parse_pdbqt_simple(file_path: Path, is_ligand: bool = True) -> List[Tuple[float, float, float]]:
    """Simple text-based parser for PDBQT files."""
    coords = []
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                record_type = line[0:6].strip()
                
                # ATOM or HETATM
                if record_type in ['ATOM', 'HETATM']:
                    # In PDBQT, ligands are typically HETATM
                    # For protein files, we want ATOM records
                    if is_ligand and record_type == 'HETATM':
                        try:
                            x = float(line[30:38].strip())
                            y = float(line[38:46].strip())
                            z = float(line[46:54].strip())
                            coords.append((x, y, z))
                        except (ValueError, IndexError):
                            continue
                    elif not is_ligand and record_type == 'ATOM':
                        try:
                            x = float(line[30:38].strip())
                            y = float(line[38:46].strip())
                            z = float(line[46:54].strip())
                            coords.append((x, y, z))
                        except (ValueError, IndexError):
                            continue
    except Exception:
        return []
    
    return coords


def _extract_from_sdf(file_path: Path) -> List[Tuple[float, float, float]]:
    """Extract coordinates from SDF file using RDKit."""
    coords = []
    
    if Chem is None:
        return []
    
    try:
        mol = Chem.MolFromMolFile(str(file_path))
        if mol is None:
            return []
        
        conf = mol.GetConformer()
        for i in range(mol.GetNumAtoms()):
            pos = conf.GetAtomPosition(i)
            coords.append((pos.x, pos.y, pos.z))
    except Exception:
        return []
    
    return coords


def _extract_from_cif(file_path: Path, is_ligand: bool = True) -> List[Tuple[float, float, float]]:
    """Extract coordinates from CIF file (simple text parsing)."""
    coords = []
    
    try:
        with open(file_path, 'r') as f:
            in_atom_site = False
            x_idx = y_idx = z_idx = -1
            
            for line in f:
                line = line.strip()
                
                if line.startswith('_atom_site.'):
                    if 'cartn_x' in line:
                        x_idx = len(line.split())
                    elif 'cartn_y' in line:
                        y_idx = len(line.split())
                    elif 'cartn_z' in line:
                        z_idx = len(line.split())
                    in_atom_site = True
                    continue
                
                if in_atom_site and line and not line.startswith('_') and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) > max(x_idx, y_idx, z_idx):
                        try:
                            x = float(parts[x_idx])
                            y = float(parts[y_idx])
                            z = float(parts[z_idx])
                            coords.append((x, y, z))
                        except (ValueError, IndexError):
                            continue
    except Exception:
        return []
    
    return coords


def _extract_from_complex(file_path: Path) -> Tuple[Optional[List[Tuple[float, float, float]]], 
                                                      Optional[List[Tuple[float, float, float]]]]:
    """
    Extract both ligand and protein coordinates from a complex file.
    
    Returns:
        Tuple of (ligand_coords, protein_coords)
    """
    ligand_coords = _extract_coordinates(file_path, is_ligand=True)
    protein_coords = _extract_coordinates(file_path, is_ligand=False)
    
    return ligand_coords, protein_coords










