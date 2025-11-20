"""Report generation module."""

import json
import pandas as pd
from pathlib import Path
from typing import Dict
from .statistics import StatisticsCalculator


class ReportGenerator:
    """Generate reports in various formats."""
    
    def __init__(self, output_dir: Path):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory to save reports.
        """
        self.output_dir = output_dir
        self.reports_dir = output_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.stats_calc = StatisticsCalculator(output_dir=output_dir)
    
    def generate_report(self, all_metrics: Dict[str, pd.DataFrame]):
        """
        Generate combined report.
        
        Args:
            all_metrics: Dictionary mapping method names to DataFrames.
        """
        # Generate JSON report
        self._generate_json_report(all_metrics)
        
        # Generate HTML report
        self._generate_html_report(all_metrics)
        
        # Generate comparison
        comparison = self.stats_calc.compare_methods(all_metrics)
        comparison_file = self.reports_dir / "method_comparison.csv"
        comparison.to_csv(comparison_file, index=False)
    
    def _generate_json_report(self, all_metrics: Dict[str, pd.DataFrame]):
        """Generate JSON report."""
        report = {}
        
        for method, df in all_metrics.items():
            stats = self.stats_calc.calculate(df)
            report[method] = {
                'count': len(df),
                'statistics': stats
            }
        
        report_file = self.reports_dir / "report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
    
    def _generate_html_report(self, all_metrics: Dict[str, pd.DataFrame]):
        """Generate HTML report."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Docking Benchmark Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>Docking Benchmark Report</h1>
        """
        
        for method, df in all_metrics.items():
            html += f"<h2>{method.upper()}</h2>"
            html += df.to_html(classes='table', table_id=f'table_{method}')
            html += "<br>"
        
        html += """
        </body>
        </html>
        """
        
        report_file = self.reports_dir / "report.html"
        with open(report_file, 'w') as f:
            f.write(html)










