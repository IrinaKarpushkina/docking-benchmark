"""Affinity extraction module."""

from pathlib import Path
from typing import Optional, Dict


def extract_affinity(
    result_path: Path,
    method: str
) -> Optional[Dict[str, float]]:
    """
    Extract affinity values from docking results.
    
    Args:
        result_path: Path to result file (log, JSON, etc.).
        method: Docking method name.
    
    Returns:
        Dictionary with affinity values, or None if extraction fails.
    """
    if method in ['qvina', 'vina']:
        return _extract_vina_affinity(result_path)
    elif method == 'boltz2':
        return _extract_boltz_affinity(result_path)
    else:
        return None


def _extract_vina_affinity(log_file: Path) -> Optional[Dict[str, float]]:
    """Extract affinity from Vina/QVina log file for the pose with minimum RMSD l.b."""
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
        return {'affinity': best_pose['affinity']}
        
    except Exception:
        pass
    return None


def _extract_boltz_affinity(json_file: Path) -> Optional[Dict[str, float]]:
    """Extract affinity from Boltz-2 JSON file."""
    try:
        import json
        with open(json_file) as f:
            data = json.load(f)
            result = {}
            if 'affinity_pred_value' in data:
                result['affinity'] = data['affinity_pred_value']
            if 'affinity_probability_binary' in data:
                result['binding_probability'] = data['affinity_probability_binary']
            return result if result else None
    except Exception:
        pass
    return None










