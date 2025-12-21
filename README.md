# Installation
### Clone the Repository
```
git clone <repository-url>
cd docking-benchmark
```
### Install common+gnina env
Create env
```
conda create -n docking_env -c conda-forge python=3.10 "numpy<2.0" pandas matplotlib seaborn pyyaml meeko rdkit scipy biopython
```
Download qvina
```
wget https://github.com/QVina/qvina/raw/master/bin/qvina02
chmod +x qvina02
./qvina02 --help
```
### Install boltz2 env
```
conda create -n boltz-env python=3.10
```
Download boltz2
```
pip install boltz[cuda] -U
```
### Install plapt env
Clone the repository
```
git clone https://github.com/trrt-good/WELP-PLAPT.git
cd WELP-PLAPT
```
Create env using Conda
```
conda env create -f environment.yml
conda activate plapt
pip install --upgrade transformers
pip install --upgrade accelerate
```
