"""Docking box preparation using Labox or default calculations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class BoxPreparator:
    """Prepare docking boxes for each protein-ligand pair."""

    def __init__(
        self,
        output_dir: Path,
        settings: Optional[Dict[str, Any]] = None,
        labox_config: Optional[Dict[str, Any]] = None,
    ):
        self.output_dir = output_dir
        self.box_dir = output_dir / "boxes"
        self.box_dir.mkdir(parents=True, exist_ok=True)

        self.settings = settings or {}
        self.labox_config = labox_config or {}
        self.summary_path = self.box_dir / "boxes_summary.json"
    
    @staticmethod
    def _normalize_protein_id(protein_id: str) -> str:
        """Normalize protein ID to lowercase for case-insensitive comparison."""
        return protein_id.lower()
    
    def _get_setting(self, protein_id: str, key: str, default: Any = None) -> Any:
        """Get setting for protein with case-insensitive lookup."""
        normalized_id = self._normalize_protein_id(protein_id)
        # Try exact match first
        if protein_id in self.settings:
            return self.settings[protein_id].get(key, default)
        # Try case-insensitive match
        for setting_key, setting_value in self.settings.items():
            if self._normalize_protein_id(setting_key) == normalized_id:
                return setting_value.get(key, default)
        return default

    def prepare(
        self,
        protein_path: Path,
        ligand_path: Optional[Path] = None,
        method: str = "labox",
    ) -> Dict[str, List[float]]:
        # Normalize protein ID for case-insensitive comparison
        normalized_id = self._normalize_protein_id(protein_path.stem)
        
        # Check if box file exists (try both original and normalized names)
        box_file = self.box_dir / f"{protein_path.stem}.json"
        normalized_box_file = self.box_dir / f"{normalized_id}.json"
        
        if box_file.exists():
            with box_file.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        elif normalized_box_file.exists():
            with normalized_box_file.open("r", encoding="utf-8") as handle:
                return json.load(handle)

        method_to_use = method or self.labox_config.get("method", "labox")

        if method_to_use == "labox":
            box_info = self._calculate_labox(protein_path)
        elif method_to_use == "autobox" and ligand_path:
            box_info = self._calculate_autobox(protein_path, ligand_path)
        else:
            fallback = self.labox_config.get("fallback_method", "default")
            if fallback == "autobox" and ligand_path:
                box_info = self._calculate_autobox(protein_path, ligand_path)
            else:
                box_info = self._default_box()

        # Save with normalized name for consistency
        final_box_file = self.box_dir / f"{normalized_id}.json"
        with final_box_file.open("w", encoding="utf-8") as handle:
            json.dump(box_info, handle, indent=2)
        
        # Also save with original name if different (for backwards compatibility)
        if normalized_id != protein_path.stem.lower():
            with box_file.open("w", encoding="utf-8") as handle:
                json.dump(box_info, handle, indent=2)

        self._update_summary(normalized_id, box_info)
        return box_info

    def _calculate_labox(self, protein_path: Path) -> Dict[str, List[float]]:
        """
        Calculate docking box using LaBOX algorithm.
        
        Implements the LaBOX algorithm (https://github.com/RyanZR/LaBOX) for calculating
        grid box center and size from protein coordinates. The algorithm computes:
        - Center: mean of min/max coordinates for each axis
        - Size: absolute difference (max - min) scaled by factor (default: 2.0)
        
        This is a direct implementation of the algorithm from LaBOX.py, not a wrapper
        around the external script.
        """
        protein_id = protein_path.stem
        normalized_id = self._normalize_protein_id(protein_id)
        # Get settings with case-insensitive lookup
        overrides = {}
        if protein_id in self.settings:
            overrides = self.settings[protein_id]
        else:
            # Try case-insensitive match
            for setting_key, setting_value in self.settings.items():
                if self._normalize_protein_id(setting_key) == normalized_id:
                    overrides = setting_value
                    break
        
        scale = overrides.get("scale", self.labox_config.get("scale", 2.0))
        min_size = overrides.get("min_size", self.labox_config.get("min_size", 4.0))

        # Try to use cleaned PDB if available, otherwise use original PDB
        source_path = self._locate_processed_protein(protein_path)
        if not source_path.exists():
            # If cleaned PDB doesn't exist yet, use original PDB
            source_path = protein_path
        
        coords = self._extract_coordinates(source_path)
        if not coords:
            raise RuntimeError(f"No coordinates found for box calculation in {source_path}")

        x_vals, y_vals, z_vals = zip(*coords)
        min_x, max_x = min(x_vals), max(x_vals)
        min_y, max_y = min(y_vals), max(y_vals)
        min_z, max_z = min(z_vals), max(z_vals)

        center = [round((min_x + max_x) / 2.0, 3), round((min_y + max_y) / 2.0, 3), round((min_z + max_z) / 2.0, 3)]
        size = [round(abs(max_x - min_x) * scale, 3), round(abs(max_y - min_y) * scale, 3), round(abs(max_z - min_z) * scale, 3)]

        # Ensure minimal size to avoid zero-width boxes
        size = [max(s, min_size) for s in size]

        return {"center": center, "size": size}

    def _calculate_autobox(self, protein_path: Path, ligand_path: Path) -> Dict[str, List[float]]:
        coords = self._extract_coordinates(ligand_path)
        if not coords:
            return self._default_box()
        x_vals, y_vals, z_vals = zip(*coords)
        center = [round(sum(x_vals) / len(x_vals), 3), round(sum(y_vals) / len(y_vals), 3), round(sum(z_vals) / len(z_vals), 3)]
        size = [round((max(x_vals) - min(x_vals)) * 2.0, 3), round((max(y_vals) - min(y_vals)) * 2.0, 3), round((max(z_vals) - min(z_vals)) * 2.0, 3)]
        return {"center": center, "size": size}

    def _default_box(self) -> Dict[str, List[float]]:
        return {"center": [0.0, 0.0, 0.0], "size": [20.0, 20.0, 20.0]}

    def _extract_coordinates(self, path: Path) -> List[Tuple[float, float, float]]:
        coords: List[Tuple[float, float, float]] = []
        if not path.exists():
            return coords

        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.startswith(("ATOM", "HETATM")):
                    continue
                try:
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    coords.append((x, y, z))
                except ValueError:
                    continue
        return coords

    def _locate_processed_protein(self, original_path: Path) -> Path:
        # Look for cleaned PDB in the shared proteins directory
        cleaned_dir = self.output_dir / "proteins" / "cleaned"
        protein_id = original_path.stem
        normalized_id = self._normalize_protein_id(protein_id)
        
        # Get chain with case-insensitive lookup
        overrides = {}
        if protein_id in self.settings:
            overrides = self.settings[protein_id]
        else:
            for setting_key, setting_value in self.settings.items():
                if self._normalize_protein_id(setting_key) == normalized_id:
                    overrides = setting_value
                    break
        
        chain = overrides.get("chain", "A") or "A"

        # Try exact match first
        candidate = cleaned_dir / f"{protein_id}_chain{chain}.pdb"
        if candidate.exists():
            return candidate
        
        # Try normalized name
        normalized_candidate = cleaned_dir / f"{normalized_id}_chain{chain}.pdb"
        if normalized_candidate.exists():
            return normalized_candidate

        # Try glob with original name
        matches = list(cleaned_dir.glob(f"{protein_id}_chain*.pdb"))
        if matches:
            return matches[0]
        
        # Try glob with normalized name (case-insensitive)
        for pdb_file in cleaned_dir.glob("*_chain*.pdb"):
            # Extract protein ID from filename (remove _chain* suffix)
            file_stem = pdb_file.stem
            # Try to extract protein ID by removing chain suffix
            for chain_suffix in ["_chainA", "_chainB", "_chainC", "_chainD", "_chainE", "_chainF"]:
                if file_stem.endswith(chain_suffix):
                    file_protein_id = file_stem[:-len(chain_suffix)]
                    if self._normalize_protein_id(file_protein_id) == normalized_id:
                        return pdb_file
            # Also try generic _chain pattern
            if "_chain" in file_stem:
                file_protein_id = file_stem.split("_chain")[0]
                if self._normalize_protein_id(file_protein_id) == normalized_id:
                    return pdb_file
        
        return original_path

    def _update_summary(self, protein_id: str, box_info: Dict[str, List[float]]) -> None:
        summary = {}
        if self.summary_path.exists():
            with self.summary_path.open("r", encoding="utf-8") as handle:
                try:
                    summary = json.load(handle)
                except json.JSONDecodeError:
                    summary = {}
        
        # Normalize protein ID for case-insensitive storage
        normalized_id = self._normalize_protein_id(protein_id)
        
        # Remove any existing entries with different case
        keys_to_remove = [k for k in summary.keys() if self._normalize_protein_id(k) == normalized_id and k != normalized_id]
        for key in keys_to_remove:
            del summary[key]
        
        summary[normalized_id] = box_info
        with self.summary_path.open("w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)





