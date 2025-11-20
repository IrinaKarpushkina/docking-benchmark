from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="docking-benchmark",
    version="0.1.0",
    author="Docking Benchmark Team",
    description="Reproducible benchmark suite for molecular docking methods",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/docking-benchmark",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "docking-benchmark=docking_benchmark.cli.run_benchmark:main",
            "docking-analyze=docking_benchmark.cli.analyze_results:main",
            "docking-compare=docking_benchmark.cli.compare_methods:main",
            "docking-build-dataset=docking_benchmark.cli.build_affinity_dataset:main",
        ],
    },
)










