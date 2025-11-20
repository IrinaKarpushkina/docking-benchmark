"""Statistical analysis module."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional


class StatisticsCalculator:
    """Calculate statistics for docking results."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize statistics calculator.
        
        Args:
            output_dir: Optional output directory for saving per-protein/ligand stats.
        """
        self.output_dir = output_dir
    
    def calculate(self, metrics_df: pd.DataFrame) -> Dict:
        """
        Calculate statistics for metrics.
        
        Args:
            metrics_df: DataFrame with metrics.
        
        Returns:
            Dictionary with statistics.
        """
        stats = {}
        
        # Calculate statistics for numeric columns
        numeric_cols = metrics_df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            stats[col] = {
                'mean': metrics_df[col].mean(),
                'std': metrics_df[col].std(),
                'min': metrics_df[col].min(),
                'max': metrics_df[col].max(),
                'median': metrics_df[col].median(),
            }
        
        return stats
    
    def compare_methods(
        self, 
        all_metrics: Dict[str, pd.DataFrame],
        metrics: Optional[List[str]] = None,
        exclude_metrics: Optional[List[str]] = None,
        aggregate_by: str = 'method',
        include_per_protein: bool = False,
        include_per_ligand: bool = False,
    ) -> pd.DataFrame:
        """
        Compare methods across metrics with customizable options.
        
        Args:
            all_metrics: Dictionary mapping method names to DataFrames.
            metrics: Specific metrics to compare (default: all numeric columns).
            exclude_metrics: Metrics to exclude from comparison.
            aggregate_by: How to aggregate ('method', 'protein', 'ligand', 'all').
            include_per_protein: Include per-protein statistics.
            include_per_ligand: Include per-ligand statistics.
        
        Returns:
            DataFrame with comparison statistics.
        """
        comparison = []
        
        # Determine which metrics to compare
        if not all_metrics:
            return pd.DataFrame()
        
        # Get all numeric columns from first DataFrame
        first_df = list(all_metrics.values())[0]
        numeric_cols = first_df.select_dtypes(include=[np.number]).columns.tolist()
        
        if metrics:
            # Filter to only requested metrics that exist
            metrics_to_use = [m for m in metrics if m in numeric_cols]
        else:
            metrics_to_use = numeric_cols
        
        if exclude_metrics:
            metrics_to_use = [m for m in metrics_to_use if m not in exclude_metrics]
        
        if not metrics_to_use:
            # Fallback to affinity if available
            if 'affinity' in numeric_cols:
                metrics_to_use = ['affinity']
            else:
                return pd.DataFrame()
        
        # Aggregate by method (default)
        for method, df in all_metrics.items():
            if len(df) == 0:
                continue
            
            stats = {'method': method, 'count': len(df)}
            
            # Calculate statistics for each metric
            for metric in metrics_to_use:
                if metric in df.columns:
                    values = df[metric].dropna()
                    if len(values) > 0:
                        stats[f'mean_{metric}'] = values.mean()
                        stats[f'std_{metric}'] = values.std()
                        stats[f'min_{metric}'] = values.min()
                        stats[f'max_{metric}'] = values.max()
                        stats[f'median_{metric}'] = values.median()
                    else:
                        stats[f'mean_{metric}'] = np.nan
                        stats[f'std_{metric}'] = np.nan
                        stats[f'min_{metric}'] = np.nan
                        stats[f'max_{metric}'] = np.nan
                        stats[f'median_{metric}'] = np.nan
            
            comparison.append(stats)
        
        result_df = pd.DataFrame(comparison)
        
        # Add per-protein statistics if requested
        if include_per_protein and 'protein' in first_df.columns:
            per_protein = []
            for method, df in all_metrics.items():
                if 'protein' not in df.columns:
                    continue
                for protein in df['protein'].unique():
                    protein_df = df[df['protein'] == protein]
                    if len(protein_df) == 0:
                        continue
                    
                    stats = {'method': method, 'protein': protein, 'count': len(protein_df)}
                    for metric in metrics_to_use:
                        if metric in protein_df.columns:
                            values = protein_df[metric].dropna()
                            if len(values) > 0:
                                stats[f'mean_{metric}'] = values.mean()
                            else:
                                stats[f'mean_{metric}'] = np.nan
                    per_protein.append(stats)
            
            if per_protein and self.output_dir:
                per_protein_df = pd.DataFrame(per_protein)
                per_protein_file = self.output_dir / "reports" / "per_protein_comparison.csv"
                per_protein_file.parent.mkdir(parents=True, exist_ok=True)
                per_protein_df.to_csv(per_protein_file, index=False)
        
        # Add per-ligand statistics if requested
        if include_per_ligand and 'ligand' in first_df.columns:
            per_ligand = []
            for method, df in all_metrics.items():
                if 'ligand' not in df.columns:
                    continue
                for ligand in df['ligand'].unique():
                    ligand_df = df[df['ligand'] == ligand]
                    if len(ligand_df) == 0:
                        continue
                    
                    stats = {'method': method, 'ligand': ligand, 'count': len(ligand_df)}
                    for metric in metrics_to_use:
                        if metric in ligand_df.columns:
                            values = ligand_df[metric].dropna()
                            if len(values) > 0:
                                stats[f'mean_{metric}'] = values.mean()
                            else:
                                stats[f'mean_{metric}'] = np.nan
                    per_ligand.append(stats)
            
            if per_ligand and self.output_dir:
                per_ligand_df = pd.DataFrame(per_ligand)
                per_ligand_file = self.output_dir / "reports" / "per_ligand_comparison.csv"
                per_ligand_file.parent.mkdir(parents=True, exist_ok=True)
                per_ligand_df.to_csv(per_ligand_file, index=False)
        
        return result_df










