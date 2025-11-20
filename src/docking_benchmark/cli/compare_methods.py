"""CLI for comparing docking methods with customizable options."""

import argparse
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional

from ..evaluation import ResultsCollector, StatisticsCalculator, ReportGenerator


def main():
    """Main CLI entry point for method comparison."""
    parser = argparse.ArgumentParser(
        description="Compare docking methods with customizable options",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument('--results-dir', type=str, required=True,
                       help='Directory with results (should contain metrics/ subdirectory)')
    
    # Output options
    parser.add_argument('--output-dir', type=str,
                       help='Output directory for reports (default: same as results-dir)')
    parser.add_argument('--output-format', nargs='+', 
                       choices=['csv', 'json', 'html', 'all'],
                       default=['csv'],
                       help='Output formats for comparison report')
    
    # Method filtering
    parser.add_argument('--methods', nargs='+',
                       choices=['qvina', 'vina', 'boltz2', 'dynamicbind',
                               'unimol', 'interformer', 'gnina', 'plapt'],
                       help='Methods to include in comparison (default: all available)')
    parser.add_argument('--exclude-methods', nargs='+',
                       choices=['qvina', 'vina', 'boltz2', 'dynamicbind',
                               'unimol', 'interformer', 'gnina', 'plapt'],
                       help='Methods to exclude from comparison')
    
    # Metric filtering
    parser.add_argument('--metrics', nargs='+',
                       help='Specific metrics to compare (e.g., affinity, rmsd)')
    parser.add_argument('--exclude-metrics', nargs='+',
                       help='Metrics to exclude from comparison')
    
    # Protein/Ligand filtering
    parser.add_argument('--proteins', nargs='+',
                       help='Filter by specific proteins')
    parser.add_argument('--ligands', nargs='+',
                       help='Filter by specific ligands')
    
    # Statistical options
    parser.add_argument('--aggregate-by', choices=['method', 'protein', 'ligand', 'all'],
                       default='method',
                       help='How to aggregate statistics')
    parser.add_argument('--include-per-protein', action='store_true',
                       help='Include per-protein statistics in comparison')
    parser.add_argument('--include-per-ligand', action='store_true',
                       help='Include per-ligand statistics in comparison')
    
    # Comparison options
    parser.add_argument('--sort-by', type=str,
                       help='Column to sort comparison by (e.g., mean_affinity)')
    parser.add_argument('--sort-order', choices=['asc', 'desc'], default='desc',
                       help='Sort order')
    parser.add_argument('--top-n', type=int,
                       help='Show only top N methods by specified metric')
    
    # Filtering options
    parser.add_argument('--min-count', type=int,
                       help='Minimum number of results required for a method to be included')
    parser.add_argument('--filter-null', action='store_true',
                       help='Exclude rows with null values in compared metrics')
    
    args = parser.parse_args()
    
    # Setup paths
    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        parser.error(f"Results directory does not exist: {results_dir}")
    
    output_dir = Path(args.output_dir) if args.output_dir else results_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load metrics
    metrics_dir = results_dir / "metrics"
    if not metrics_dir.exists():
        parser.error(f"Metrics directory not found: {metrics_dir}")
    
    print("=" * 80)
    print("METHOD COMPARISON")
    print("=" * 80)
    print(f"Results directory: {results_dir}")
    print(f"Output directory: {output_dir}")
    print("=" * 80)
    
    # Load all available metrics
    all_metrics = {}
    for metrics_file in metrics_dir.glob("metrics_*.csv"):
        method = metrics_file.stem.replace("metrics_", "")
        df = pd.read_csv(metrics_file)
        all_metrics[method] = df
        print(f"  Loaded {len(df)} results for {method}")
    
    if not all_metrics:
        parser.error(f"No metrics files found in {metrics_dir}")
    
    # Apply method filtering
    if args.methods:
        all_metrics = {k: v for k, v in all_metrics.items() if k in args.methods}
    
    if args.exclude_methods:
        all_metrics = {k: v for k, v in all_metrics.items() if k not in args.exclude_methods}
    
    if not all_metrics:
        parser.error("No methods remaining after filtering")
    
    # Apply protein/ligand filtering
    if args.proteins or args.ligands:
        for method in all_metrics:
            df = all_metrics[method]
            if args.proteins:
                df = df[df['protein'].isin(args.proteins)]
            if args.ligands:
                df = df[df['ligand'].isin(args.ligands)]
            all_metrics[method] = df
    
    # Apply null filtering
    if args.filter_null:
        for method in list(all_metrics.keys()):
            df = all_metrics[method]
            if args.metrics:
                # Filter nulls only in specified metrics
                df = df.dropna(subset=args.metrics)
            else:
                # Filter nulls in all numeric columns
                numeric_cols = df.select_dtypes(include=['number']).columns
                df = df.dropna(subset=numeric_cols)
            if len(df) == 0:
                del all_metrics[method]
                print(f"  Warning: {method} has no valid results after filtering")
            else:
                all_metrics[method] = df
    
    # Apply minimum count filter
    if args.min_count:
        for method in list(all_metrics.keys()):
            if len(all_metrics[method]) < args.min_count:
                del all_metrics[method]
                print(f"  Warning: {method} has fewer than {args.min_count} results, excluded")
    
    if not all_metrics:
        parser.error("No methods remaining after filtering")
    
    print(f"\nComparing {len(all_metrics)} methods: {', '.join(all_metrics.keys())}")
    
    # Initialize calculator and generator
    stats_calc = StatisticsCalculator(output_dir=output_dir)
    reporter = ReportGenerator(output_dir)
    
    # Generate comparison
    print("\n" + "=" * 80)
    print("GENERATING COMPARISON")
    print("=" * 80)
    
    comparison_options = {
        'metrics': args.metrics,
        'exclude_metrics': args.exclude_metrics,
        'aggregate_by': args.aggregate_by,
        'include_per_protein': args.include_per_protein,
        'include_per_ligand': args.include_per_ligand,
    }
    
    comparison = stats_calc.compare_methods(all_metrics, **comparison_options)
    
    # Apply sorting
    if args.sort_by and args.sort_by in comparison.columns:
        ascending = (args.sort_order == 'asc')
        comparison = comparison.sort_values(by=args.sort_by, ascending=ascending)
    
    # Apply top N filter
    if args.top_n:
        comparison = comparison.head(args.top_n)
    
    # Save comparison
    if 'csv' in args.output_format or 'all' in args.output_format:
        comparison_file = output_dir / "reports" / "method_comparison.csv"
        comparison_file.parent.mkdir(parents=True, exist_ok=True)
        comparison.to_csv(comparison_file, index=False)
        print(f"  Saved CSV comparison to: {comparison_file}")
    
    # Generate full reports if requested
    if 'json' in args.output_format or 'html' in args.output_format or 'all' in args.output_format:
        reporter.generate_report(all_metrics)
        if 'json' in args.output_format or 'all' in args.output_format:
            print(f"  Saved JSON report to: {output_dir / 'reports' / 'report.json'}")
        if 'html' in args.output_format or 'all' in args.output_format:
            print(f"  Saved HTML report to: {output_dir / 'reports' / 'report.html'}")
    
    # Print comparison
    print("\n" + "=" * 80)
    print("COMPARISON RESULTS")
    print("=" * 80)
    print(comparison.to_string(index=False))
    print("=" * 80)
    
    print(f"\nComparison complete! Results saved to {output_dir / 'reports'}")


if __name__ == '__main__':
    main()

