FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy environment file
COPY environment.yml .

# Create conda environment
RUN conda env create -f environment.yml && \
    conda clean -afy

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "docking-benchmark", "/bin/bash", "-c"]

# Copy project files
COPY . .

# Install the package
RUN pip install -e .

# Set environment variables
ENV PATH /opt/conda/envs/docking-benchmark/bin:$PATH

# Default command
CMD ["bash"]










