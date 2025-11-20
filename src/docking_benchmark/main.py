"""
Main module for docking benchmark pipeline.

This module contains the DockingBenchmark class that orchestrates
the three-stage pipeline: preprocessing, docking, and metrics extraction.
"""

import argparse
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional

from .config import load_config, load_methods_config
from .preprocessing import ProteinPreparator, LigandPreparator, BoxPreparator
from .docking import (
    QVinaDocker, VinaDocker, Boltz2Docker,
    DynamicBindDocker, UniMolDocker, InterformerDocker,
    GninaDocker, PLAPTDocker
)
from .evaluation import ResultsCollector
from .utils import load_protein_settings, load_box_settings


class DockingBenchmark:
    """Main class for running docking benchmarks."""
    
    def __init__(self, config: Optional[Dict] = None, args: Optional[argparse.Namespace] = None):
        """
        Initialize the benchmark.
        
        Args:
            config: Configuration dictionary. If None, loads from default config.
            args: Command line arguments. Takes precedence over config.
        """
        # Load configuration
        if config is None:
            config = load_config()
        
        self.config = config
        self.methods_config = load_methods_config()
        
        # Override with command line arguments if provided
        if args is not None:
            self._apply_args(args)
        
        # Set random seed
        self.random_seed = self.config.get('random_state', 42)
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)
        
        # Setup directories
        self.base_dir = Path(self.config['base_dir'])
        self.protein_dir = Path(self.config['protein_dir'])
        self.ligand_dir = Path(self.config['ligand_dir'])
        self.output_dir = self.base_dir / self.config.get('output_dir', 'results')
        self.processed_dir = self.base_dir / self.config.get('processed_dir', 'processed')
        
        # Create directories
        for dir_path in [self.output_dir, self.processed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Methods to run
        self.methods = self.config.get('methods', [])
        
        # Get preprocessing environment
        env_config = self.config.get('environments', {})
        self.preprocessing_env = env_config.get('preprocessing', None)

        # Load optional preparation settings
        protein_settings_path = self.config.get('protein_settings_file')
        box_settings_path = self.config.get('box_settings_file')
        self.protein_settings = load_protein_settings(protein_settings_path)
        self.box_settings = load_box_settings(box_settings_path)
        self.labox_config = self.config.get('labox', {})

        # Initialize preparators
        self.protein_prep = ProteinPreparator(
            self.processed_dir,
            settings=self.protein_settings,
            labox_config=self.labox_config,
        )
        self.ligand_prep = LigandPreparator(self.processed_dir)
        self.box_prep = BoxPreparator(
            self.processed_dir,
            settings=self.box_settings,
            labox_config=self.labox_config,
        )
        
        # Initialize dockers
        self.dockers = self._initialize_dockers()
        
        # Initialize results collector (reporting is done separately)
        self.collector = ResultsCollector(self.output_dir)
    
    def _apply_args(self, args: argparse.Namespace):
        """Apply command line arguments to config."""
        if hasattr(args, 'base_dir') and args.base_dir:
            self.config['base_dir'] = args.base_dir
        if hasattr(args, 'protein_dir') and args.protein_dir:
            self.config['protein_dir'] = args.protein_dir
        if hasattr(args, 'ligand_dir') and args.ligand_dir:
            self.config['ligand_dir'] = args.ligand_dir
        if hasattr(args, 'random_state') and args.random_state:
            self.config['random_state'] = args.random_state
        if hasattr(args, 'methods') and args.methods:
            self.config['methods'] = args.methods
    
    def _initialize_dockers(self) -> Dict:
        """Initialize docker instances for each method."""
        dockers = {}
        
        for method in self.methods:
            method_config = self.methods_config.get(method, {})

            method_config.setdefault('labox', self.labox_config)
            method_config.setdefault('protein_settings', self.protein_settings)
            method_config.setdefault('box_settings', self.box_settings)
            
            if method == 'qvina':
                dockers[method] = QVinaDocker(method_config, self.processed_dir, self.output_dir, 
                                             preprocessing_env=self.preprocessing_env)
            elif method == 'vina':
                dockers[method] = VinaDocker(method_config, self.processed_dir, self.output_dir,
                                           preprocessing_env=self.preprocessing_env)
            elif method == 'boltz2':
                dockers[method] = Boltz2Docker(method_config, self.processed_dir, self.output_dir,
                                              preprocessing_env=self.preprocessing_env)
            elif method == 'dynamicbind':
                dockers[method] = DynamicBindDocker(method_config, self.processed_dir, self.output_dir,
                                                    preprocessing_env=self.preprocessing_env)
            elif method == 'unimol':
                dockers[method] = UniMolDocker(method_config, self.processed_dir, self.output_dir,
                                              preprocessing_env=self.preprocessing_env)
            elif method == 'interformer':
                dockers[method] = InterformerDocker(method_config, self.processed_dir, self.output_dir,
                                                    preprocessing_env=self.preprocessing_env)
            elif method == 'gnina':
                dockers[method] = GninaDocker(method_config, self.processed_dir, self.output_dir,
                                             preprocessing_env=self.preprocessing_env)
            elif method == 'plapt':
                dockers[method] = PLAPTDocker(method_config, self.processed_dir, self.output_dir,
                                             preprocessing_env=self.preprocessing_env)
        
        return dockers
    
    def run(self):
        """Run the complete benchmarking pipeline."""
        print("=" * 80)
        print("DOCKING BENCHMARK PIPELINE")
        print("=" * 80)
        print(f"Random seed: {self.random_seed}")
        print(f"Methods to run: {', '.join(self.methods)}")
        print(f"Protein directory: {self.protein_dir}")
        print(f"Ligand directory: {self.ligand_dir}")
        print("=" * 80)
        
        # Stage 1: Preprocessing
        print("\n" + "=" * 80)
        print("STAGE 1: PREPROCESSING")
        print("=" * 80)
        self.preprocess_all()
        
        # Stage 2: Docking
        print("\n" + "=" * 80)
        print("STAGE 2: DOCKING")
        print("=" * 80)
        self.dock_all()
        
        # Stage 3: Metrics extraction
        print("\n" + "=" * 80)
        print("STAGE 3: METRICS EXTRACTION")
        print("=" * 80)
        self.extract_metrics_all()
        
        print("\n" + "=" * 80)
        print("BENCHMARK COMPLETE!")
        print("=" * 80)
    
    def preprocess_all(self):
        """Run preprocessing for all selected methods."""
        for method in self.methods:
            print(f"\n[Preprocessing] {method.upper()}")
            try:
                docker = self.dockers.get(method)
                if docker:
                    docker.preprocess(self.protein_dir, self.ligand_dir)
                else:
                    print(f"  Warning: No docker found for {method}")
            except Exception as e:
                print(f"  Error in preprocessing {method}: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    def dock_all(self):
        """Run docking for all selected methods."""
        for method in self.methods:
            print(f"\n[Docking] {method.upper()}")
            try:
                docker = self.dockers.get(method)
                if docker:
                    # Pass ligand_dir for error logging
                    docker.dock_all(ligand_dir=self.ligand_dir)
                else:
                    print(f"  Warning: No docker found for {method}")
            except Exception as e:
                print(f"  Error in docking {method}: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    def extract_metrics_all(self):
        """Extract metrics for all selected methods."""
        for method in self.methods:
            print(f"\n[Metrics] {method.upper()}")
            try:
                docker = self.dockers.get(method)
                if docker:
                    metrics = docker.extract_metrics()
                    self.collector.collect(method, metrics)
                else:
                    print(f"  Warning: No docker found for {method}")
            except Exception as e:
                print(f"  Error in metrics extraction {method}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Note: Method comparison is now done separately via compare_methods script
        print("\n[Metrics] Metrics extraction complete. Use compare_methods script for comparison.")

