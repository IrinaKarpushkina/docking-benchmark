"""Base class for docking methods."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

from ..utils.env_utils import run_in_env
import subprocess


class BaseDocker(ABC):
    """Base class for all docking methods."""
    
    def __init__(self, config: Dict, processed_dir: Path, output_dir: Path, 
                 preprocessing_env: Optional[str] = None):
        """
        Initialize docker.
        
        Args:
            config: Method-specific configuration.
            processed_dir: Directory with prepared files.
            output_dir: Directory for output results.
            preprocessing_env: Conda environment for preprocessing.
        """
        self.config = config
        self.processed_dir = processed_dir
        self.output_dir = output_dir
        self.method_name = self.__class__.__name__.replace('Docker', '').lower()
        
        # Environment configuration
        self.preprocessing_env = preprocessing_env
        self.docking_env = config.get('conda_env', None) or preprocessing_env
    
    def run_command_in_env(self, command: List[str], use_docking_env: bool = True) -> subprocess.CompletedProcess:
        """
        Run command in appropriate environment.
        
        Args:
            command: Command to run.
            use_docking_env: If True, use docking environment; if False, use preprocessing env.
        
        Returns:
            CompletedProcess result.
        """
        import subprocess
        env_name = self.docking_env if use_docking_env else self.preprocessing_env
        return run_in_env(command, env_name=env_name)
    
    @abstractmethod
    def preprocess(self, protein_dir: Path, ligand_dir: Path):
        """
        Preprocess input files for this method.
        
        Args:
            protein_dir: Directory with protein files.
            ligand_dir: Directory with ligand files.
        """
        pass
    
    @abstractmethod
    def dock_all(self, ligand_dir: Optional[Path] = None):
        """
        Run docking for all protein-ligand pairs.
        
        Args:
            ligand_dir: Optional directory containing ligand CSV files for error logging.
        """
        pass
    
    @abstractmethod
    def extract_metrics(self) -> List[Dict]:
        """
        Extract metrics from docking results.
        
        Returns:
            List of dictionaries with metrics for each docking.
        """
        pass

