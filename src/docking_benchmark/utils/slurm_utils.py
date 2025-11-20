"""SLURM utility functions."""

from pathlib import Path
from typing import List, Dict
import yaml


def create_slurm_script(
    job_name: str,
    commands: List[str],
    config: Dict,
    output_file: Path
):
    """
    Create SLURM submission script.
    
    Args:
        job_name: Job name.
        commands: List of commands to execute.
        config: SLURM configuration dictionary.
        output_file: Path to output script file.
    """
    script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --time={config.get('time', '24:00:00')}
#SBATCH --nodes={config.get('nodes', 1)}
#SBATCH --ntasks-per-node={config.get('ntasks_per_node', 1)}
#SBATCH --cpus-per-task={config.get('cpus_per_task', 8)}
#SBATCH --mem={config.get('mem', '32G')}
#SBATCH --partition={config.get('partition', 'gpu')}
"""
    
    if config.get('gpus', 0) > 0:
        script += f"#SBATCH --gres=gpu:{config.get('gpus', 1)}\n"
    
    script += f"""
#SBATCH --output={output_file.parent / f'{job_name}.out'}
#SBATCH --error={output_file.parent / f'{job_name}.err'}

"""
    
    for cmd in commands:
        script += f"{cmd}\n"
    
    with open(output_file, 'w') as f:
        f.write(script)
    
    output_file.chmod(0o755)










