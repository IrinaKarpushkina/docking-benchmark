"""Environment management utilities."""

import subprocess
import os
from pathlib import Path
from typing import Optional, List


def get_conda_env_command(env_name: Optional[str] = None) -> List[str]:
    """
    Get command to run in conda environment.
    
    Args:
        env_name: Name of conda environment. If None, uses current environment.
    
    Returns:
        Command prefix to activate conda environment.
    """
    if env_name is None or env_name == "":
        return []
    
    # Check if conda is available
    try:
        subprocess.run(["conda", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    
    # Return conda run command
    return ["conda", "run", "-n", env_name, "--no-capture-output"]


def run_in_env(
    command: List[str],
    env_name: Optional[str] = None,
    cwd: Optional[Path] = None,
    check: bool = True,
    capture_output: bool = False,
    timeout: Optional[float] = None
) -> subprocess.CompletedProcess:
    """
    Run command in specified conda environment.
    
    Args:
        command: Command to run.
        env_name: Conda environment name. If None, runs in current environment.
        cwd: Working directory.
        check: Whether to check return code.
        capture_output: Whether to capture output.
        timeout: Maximum time in seconds to wait for command. If None, no timeout.
    
    Returns:
        CompletedProcess result.
    
    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout.
    """
    if env_name and env_name != "":
        # Use conda run
        full_command = ["conda", "run", "-n", env_name, "--no-capture-output"] + command
    else:
        full_command = command
    
    return subprocess.run(
        full_command,
        cwd=cwd,
        check=check,
        capture_output=capture_output,
        text=True,
        timeout=timeout
    )


def check_env_exists(env_name: str) -> bool:
    """
    Check if conda environment exists.
    
    Args:
        env_name: Name of conda environment.
    
    Returns:
        True if environment exists.
    """
    try:
        result = subprocess.run(
            ["conda", "env", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        return env_name in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_python_in_env(env_name: Optional[str] = None) -> str:
    """
    Get Python executable path in conda environment.
    
    Args:
        env_name: Name of conda environment. If None, returns current Python.
    
    Returns:
        Path to Python executable.
    """
    if env_name and env_name != "":
        # Get Python from conda env
        try:
            result = subprocess.run(
                ["conda", "run", "-n", env_name, "which", "python"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            # Fallback to python3
            return "python3"
    else:
        return "python3"










