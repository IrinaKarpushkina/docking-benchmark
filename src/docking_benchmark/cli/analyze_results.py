"""CLI for analyzing results."""

import argparse
import pandas as pd
from pathlib import Path

from ..evaluation import ResultsCollector, StatisticsCalculator, ReportGenerator


def main():
    """Main CLI entry point for result analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze docking benchmark results"
    )
    
    parser.add_argument('--results-dir', type=str, required=True,
                       help='Directory with results')
    parser.add_argument('--output-dir', type=str,
                       help='Output directory for reports')
    
    args = parser.parse_args()
    
    results_dir = Path(args.results_dir)
    output_dir = Path(args.output_dir) if args.output_dir else results_dir
    
    # Load metrics
    metrics_dir = results_dir / "metrics"
    all_metrics = {}
    
    for metrics_file in metrics_dir.glob("metrics_*.csv"):
        method = metrics_file.stem.replace("metrics_", "")
        df = pd.read_csv(metrics_file)
        all_metrics[method] = df
    
    # Generate reports
    reporter = ReportGenerator(output_dir)
    reporter.generate_report(all_metrics)
    
    # Calculate statistics
    stats_calc = StatisticsCalculator(output_dir=output_dir)
    comparison = stats_calc.compare_methods(all_metrics)
    
    print("\nMethod Comparison:")
    print(comparison.to_string(index=False))


if __name__ == '__main__':
    main()










