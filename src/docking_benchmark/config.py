"""Configuration loading and management."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file. If None, uses default.
    
    Returns:
        Dictionary with configuration.
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "default_config.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def load_methods_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load methods configuration.
    
    Args:
        config_path: Path to methods config file. If None, uses default.
    
    Returns:
        Dictionary with methods configuration.
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "methods_config.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def load_slurm_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load SLURM configuration.
    
    Args:
        config_path: Path to SLURM config file. If None, uses default.
    
    Returns:
        Dictionary with SLURM configuration.
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "slurm_config.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config










