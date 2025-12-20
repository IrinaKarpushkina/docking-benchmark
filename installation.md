### Create the environment 
```
conda activate dock-bench-v2
```
```
conda install conda-forge::qvina
```
```
conda install -c conda-forge rdkit biopython pandas numpy matplotlib seaborn
```
```
pip install meeko
```
### To install gnina

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
```
### To install plapt
