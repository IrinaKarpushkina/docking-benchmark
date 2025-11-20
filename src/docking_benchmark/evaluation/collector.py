"""Results collection module."""

import pandas as pd
from pathlib import Path
from typing import Dict, List


class ResultsCollector:
    """Collect and aggregate results from all methods."""
    
    def __init__(self, output_dir: Path):
        """
        Initialize results collector.
        
        Args:
            output_dir: Directory to save collected results.
        """
        self.output_dir = output_dir
        self.metrics_dir = output_dir / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        self.all_metrics = {}
    
    def collect(self, method: str, metrics: List[Dict]):
        """
        Collect metrics for a method.
        
        Args:
            method: Method name.
            metrics: List of metric dictionaries.
        """
        if not metrics:
            return
        
        df = pd.DataFrame(metrics)
        output_file = self.metrics_dir / f"metrics_{method}.csv"
        df.to_csv(output_file, index=False)
        
        self.all_metrics[method] = df
        print(f"  Collected {len(metrics)} metrics for {method}")
    
    def get_all_metrics(self) -> Dict[str, pd.DataFrame]:
        """Get all collected metrics."""
        return self.all_metrics
    
    def combine_all(self) -> pd.DataFrame:
        """Combine all metrics into a single DataFrame."""
        if not self.all_metrics:
            return pd.DataFrame()
        
        combined = pd.concat(self.all_metrics.values(), ignore_index=True)
        output_file = self.metrics_dir / "metrics_all.csv"
        combined.to_csv(output_file, index=False)
        
        return combined










