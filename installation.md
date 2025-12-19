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
conda install cudatoolkit=11.5 -c nvidia
```
Установка OpenBabel
```
conda install -c conda-forge openbabel
```
