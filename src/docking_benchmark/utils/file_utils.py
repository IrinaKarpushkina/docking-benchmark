"""File utility functions."""

from pathlib import Path
from typing import List, Optional


def ensure_dir(dir_path: Path):
    """Ensure directory exists, create if not."""
    dir_path.mkdir(parents=True, exist_ok=True)


def find_files(
    directory: Path,
    pattern: str,
    recursive: bool = True
) -> List[Path]:
    """
    Find files matching pattern.
    
    Args:
        directory: Directory to search.
        pattern: File pattern (e.g., "*.pdb", "*.sdf").
        recursive: Search recursively.
    
    Returns:
        List of matching file paths.
    """
    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    return file_path.stat().st_size










