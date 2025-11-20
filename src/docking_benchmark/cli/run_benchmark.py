"""CLI for running benchmarks."""

import argparse
from pathlib import Path

from ..main import DockingBenchmark
from ..config import load_config, load_methods_config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run docking benchmark",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # General arguments
    parser.add_argument('--base-dir', type=str,
                       help='Base directory for output and processed files')
    parser.add_argument('--protein-dir', type=str,
                       help='Directory containing protein PDB files')
    parser.add_argument('--ligand-dir', type=str,
                       help='Directory containing ligand SDF files')
    parser.add_argument('--random-state', type=int,
                       help='Random seed for reproducibility')
    parser.add_argument('--methods', nargs='+',
                       choices=['qvina', 'vina', 'boltz2', 'dynamicbind',
                               'unimol', 'interformer', 'gnina', 'plapt'],
                       help='Docking methods to run')
    parser.add_argument('--protein-settings', type=str,
                       help='Path to protein preparation overrides (YAML/JSON)')
    parser.add_argument('--box-settings', type=str,
                       help='Path to box preparation overrides (YAML/JSON)')
    
    # Config files
    parser.add_argument('--config', type=str,
                       help='Path to config YAML file')
    parser.add_argument('--methods-config', type=str,
                       help='Path to methods config YAML file')
    
    # QVina arguments
    parser.add_argument('--qvina-binary', type=str,
                       help='Path to QVina binary')
    parser.add_argument('--qvina-exhaustiveness', type=int,
                       help='QVina exhaustiveness parameter')
    
    # Vina arguments
    parser.add_argument('--vina-binary', type=str,
                       help='Path to AutoDock Vina binary')
    parser.add_argument('--vina-exhaustiveness', type=int,
                       help='Vina exhaustiveness parameter')
    
    # Boltz-2 arguments
    parser.add_argument('--boltz-use-msa-server', action='store_true',
                       help='Use MSA server for Boltz-2')
    parser.add_argument('--boltz-no-msa-server', dest='boltz_use_msa_server',
                       action='store_false', help='Disable MSA server for Boltz-2')
    parser.add_argument('--boltz-use-potentials', action='store_true',
                       help='Use inference-time potentials for Boltz-2')
    parser.add_argument('--boltz-no-potentials', dest='boltz_use_potentials',
                       action='store_false', help='Disable potentials for Boltz-2')
    
    args = parser.parse_args()
    
    # Load config
    if args.config:
        config = load_config(Path(args.config))
    else:
        config = load_config()
    
    # Override with command line arguments
    if args.base_dir:
        config['base_dir'] = args.base_dir
    if args.protein_dir:
        config['protein_dir'] = args.protein_dir
    if args.ligand_dir:
        config['ligand_dir'] = args.ligand_dir
    if args.random_state:
        config['random_state'] = args.random_state
    if args.methods:
        config['methods'] = args.methods
    if args.protein_settings:
        config['protein_settings_file'] = args.protein_settings
    if args.box_settings:
        config['box_settings_file'] = args.box_settings
    
    # Load methods config
    if args.methods_config:
        methods_config = load_methods_config(Path(args.methods_config))
    else:
        methods_config = load_methods_config()
    
    # Override methods config with CLI args
    if args.qvina_binary:
        methods_config.setdefault('qvina', {})['binary'] = args.qvina_binary
    if args.qvina_exhaustiveness:
        methods_config.setdefault('qvina', {})['exhaustiveness'] = args.qvina_exhaustiveness
    
    if args.vina_binary:
        methods_config.setdefault('vina', {})['binary'] = args.vina_binary
    if args.vina_exhaustiveness:
        methods_config.setdefault('vina', {})['exhaustiveness'] = args.vina_exhaustiveness
    
    if hasattr(args, 'boltz_use_msa_server'):
        methods_config.setdefault('boltz2', {})['use_msa_server'] = args.boltz_use_msa_server
    if hasattr(args, 'boltz_use_potentials'):
        methods_config.setdefault('boltz2', {})['use_potentials'] = args.boltz_use_potentials
    
    # Create and run benchmark
    benchmark = DockingBenchmark(config=config, args=args)
    benchmark.run()


if __name__ == '__main__':
    main()





