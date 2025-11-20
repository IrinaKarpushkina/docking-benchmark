# Contributing

## Development Setup

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Adding a New Docking Method

1. Create a new file in `src/docking_benchmark/docking/`:
   ```python
   from .base import BaseDocker
   
   class NewMethodDocker(BaseDocker):
       def preprocess(self, protein_dir, ligand_dir):
           # Implement preprocessing
           pass
       
       def dock_all(self):
           # Implement docking
           pass
       
       def extract_metrics(self):
           # Extract metrics
           return []
   ```

2. Add method to `docking/__init__.py`
3. Add configuration to `config/methods_config.yaml`
4. Update `main.py` to include the new method

## Running Tests

```bash
pytest tests/
```

## Code Style

- Use `black` for formatting
- Use `flake8` for linting
- Follow PEP 8 style guide

## Submitting Changes

1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request










