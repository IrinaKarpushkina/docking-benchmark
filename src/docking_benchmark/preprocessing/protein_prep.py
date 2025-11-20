"""Protein preparation module using Meeko."""

from __future__ import annotations

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any


class ProteinPreparator:
    """Prepare protein structures for docking."""

    def __init__(
        self,
        output_dir: Path,
        settings: Optional[Dict[str, Any]] = None,
        labox_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the protein preparator."""
        self.output_dir = output_dir
        self.protein_dir = output_dir / "proteins"
        self.clean_dir = self.protein_dir / "cleaned"
        self.protein_dir.mkdir(parents=True, exist_ok=True)
        self.clean_dir.mkdir(parents=True, exist_ok=True)

        self.settings = settings or {}
        self.labox_config = labox_config or {}

        self.meeko_cli = self._locate_meeko_cli()
        if self.meeko_cli is None:
            raise FileNotFoundError(
                "Vendored Meeko CLI script not found. Expected mk_prepare_receptor.py "
                "under src/external/meeko/cli or src/docking_benchmark/external/meeko/cli."
            )

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
    
    def prepare(self, pdb_path: Path, method: str = "all") -> Dict[str, Path]:
        """Prepare the requested protein for docking methods."""
        results: Dict[str, Path] = {}

        if method in {"qvina", "vina", "gnina"}:
            protein_id = pdb_path.stem
            normalized_id = self._normalize_protein_id(protein_id)
            
            # Get settings with case-insensitive lookup
            chain_id = self._get_setting(protein_id, "chain", "A") or "A"
            include_het = self._get_setting(protein_id, "include_ligands", False)
            include_cofactors = self._get_setting(protein_id, "include_cofactors", False)
            include_waters = self._get_setting(protein_id, "include_waters", False)

            # Use normalized name for file storage
            cleaned_pdb = self.clean_dir / f"{normalized_id}_chain{chain_id}.pdb"
            self._generate_clean_pdb(
                pdb_path,
                cleaned_pdb,
                chain_id=chain_id,
                include_het=include_het,
                include_cofactors=include_cofactors,
                include_waters=include_waters,
            )

            # Use normalized name for PDBQT file
            pdbqt_path = self.protein_dir / f"{normalized_id}.pdbqt"
            if not pdbqt_path.exists() or pdbqt_path.stat().st_size == 0:
                self._run_meeko_receptor(cleaned_pdb, pdbqt_path, chain_id)

            results[method] = pdbqt_path

        return results

    def _locate_meeko_cli(self) -> Optional[Path]:
        """Return the vendored Meeko CLI path if available."""
        candidates = []
        base = Path(__file__).resolve()
        candidates.append(
            base.parents[2] / "external" / "meeko" / "cli" / "mk_prepare_receptor.py"
        )  # .../src/external
        candidates.append(
            base.parents[1] / "external" / "meeko" / "cli" / "mk_prepare_receptor.py"
        )  # .../src/docking_benchmark/external

        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _generate_clean_pdb(
        self,
        source: Path,
        destination: Path,
        chain_id: str,
        include_het: bool,
        include_cofactors: bool,
        include_waters: bool,
    ) -> None:
        """Filter the original PDB to the requested chain and optional records."""
        chain_id = chain_id.strip() or "A"
        selected_lines = []
        chain_col = 21
        record_whitelist = {"ATOM"}

        if include_het or include_cofactors:
            record_whitelist.add("HETATM")

        with source.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.startswith(("ATOM", "HETATM")):
                    continue

                if line.startswith("HETATM") and "HETATM" not in record_whitelist:
                    continue

                if not include_waters and line[17:20].strip() == "HOH":
                    continue

                if line[chain_col].strip() != chain_id:
                    continue

                selected_lines.append(line)

        if not selected_lines:
            raise RuntimeError(
                f"No atoms selected for {source.name} with chain '{chain_id}'."
            )

        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as handle:
            handle.writelines(selected_lines)

    def _run_meeko_receptor(self, cleaned_pdb: Path, pdbqt_path: Path, chain_id: str) -> None:
        """Invoke the vendored Meeko CLI to generate the receptor PDBQT."""
        env = os.environ.copy()
        meeko_root = str(self.meeko_cli.parents[2])  # directory containing 'meeko'
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{meeko_root}{os.pathsep}{existing}" if existing else meeko_root

        cmd = [
            sys.executable,
            str(self.meeko_cli),
            "--read_pdb",
            str(cleaned_pdb),
            "--default_altloc",
            chain_id,
            "--delete_residues",
            "HOH",
            "--allow_bad_res",
            "-p",
            str(pdbqt_path),
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
            if pdbqt_path.exists() and pdbqt_path.stat().st_size > 0:
                print(f"    [PREPARATION] Protein {pdbqt_path.stem}: prepared using Meeko")
        except subprocess.CalledProcessError as exc:
            try:
                self._fallback_receptor_prep(cleaned_pdb, pdbqt_path)
                return
            except Exception as fallback_exc:
                raise RuntimeError(
                    f"Meeko receptor preparation failed for {cleaned_pdb.name}: {exc.stderr}"
                ) from fallback_exc

        if not pdbqt_path.exists() or pdbqt_path.stat().st_size == 0:
            try:
                self._fallback_receptor_prep(cleaned_pdb, pdbqt_path)
            except Exception as fallback_exc:
                raise RuntimeError(
                    f"Meeko receptor preparation produced an empty file: {pdbqt_path}"
                ) from fallback_exc

    def _fallback_receptor_prep(self, cleaned_pdb: Path, pdbqt_path: Path) -> None:
        """Fallback to Open Babel conversion when Meeko is unavailable."""
        try:
            subprocess.run(
                [
                    "obabel",
                    str(cleaned_pdb),
                    "-O",
                    str(pdbqt_path),
                    "-xr",
                    "-xh",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            if pdbqt_path.exists() and pdbqt_path.stat().st_size > 0:
                print(f"    [PREPARATION] Protein {pdbqt_path.stem}: prepared using Open Babel (fallback)")
        except FileNotFoundError as exc:
            raise RuntimeError("Open Babel (obabel) is required for receptor fallback preparation") from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Open Babel receptor conversion failed: {exc.stderr}") from exc
        if not pdbqt_path.exists() or pdbqt_path.stat().st_size == 0:
            raise RuntimeError(f"Open Babel receptor conversion produced an empty file: {pdbqt_path}")

    def export_preparation_manifest(self) -> Path:
        """Persist preparation metadata for downstream steps."""
        manifest_path = self.output_dir / "proteins" / "preparation_manifest.json"
        metadata = {
            "settings": self.settings,
            "labox": self.labox_config,
        }
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with manifest_path.open("w", encoding="utf-8") as handle:
            json.dump(metadata, handle, indent=2)
        return manifest_path

