# Installation
### Clone the Repository
```
git clone <repository-url>
cd docking-benchmark
```
### Install common+qvina env
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
### Install gnina env
Create env
```
conda create -n gnina python=3.10
conda activate gnina
```
Поиск пути к CUDA
```
find /usr -name libcudart.so 2>/dev/null
```
на сервере aicltr это /usr/lib/x86_64-linux-gnu/libcudart.so
Далее нужно прописать путь в bashrc:
```
nano ~/.bashrc
```
И в конец файла вставить:
```
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
```
Установка дополнительных зависимостей
```
conda install -c conda-forge boost eigen glog protobuf hdf5 openblas cmake git make jsoncpp pytest
```
```
conda install -c conda-forge cuda-runtime=12.4
```
Установка OpenBabel
```
conda install -c conda-forge openbabel
```
```
conda env config vars set LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
```
Установка исполняемого файла gnina
```
mkdir -p bin
wget https://github.com/gnina/gnina/releases/download/v1.3/gnina -O ./bin/gnina
chmod +x ./bin/gnina

# Добавлено в ~/.bashrc для вызова команды 'gnina' из любого места:
export PATH="/mnt/tank/scratch/ikarpushkina/docking-benchmark-2/bin:$PATH"

### Install DynamicBind env
Clone the repository
```
git clone https://github.com/luwei0917/DynamicBind.git
cd DynamicBind
```
Create a new environment for inference. While in the project directory run
```
conda env create -f environment.yml
```
Create a new environment for structural Relaxation.
```
conda create --name relax python=3.8
conda activate relax
```
Install dependencies
```
conda install -c conda-forge openmm pdbfixer libstdcxx-ng openmmforcefields openff-toolkit ambertools=22 compilers biopython
```
Checkpoints Download
Download and unzip the workdir.zip containing the model checkpoint form https://zenodo.org/records/10137507, v2 is contained here https://zenodo.org/records/10183369.
