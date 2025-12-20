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

To install PLAPT
Клонирование репозитория и переход в папку
code
Bash
# Перейдите в корень вашего проекта
cd /mnt/tank/scratch/ikarpushkina/docking-benchmark-2/
git clone https://github.com/Bindwell/PLAPT.git
cd PLAPT
Подготовка окружения (очистка от конфликтов)
code
Bash
conda activate dock-bench-v2
# Удаляем старые версии torch, если они были, чтобы избежать конфликта "iJIT_NotifyEvent"
pip uninstall -y torch torchvision torchaudio
conda remove -y mkl mkl-service intel-openmp
Установка стабильного PyTorch и библиотек MKL
Мы устанавливаем PyTorch через pip со специфическим индексом CUDA 12.1 — это самый надежный способ для работы на вашем кластере.
code
Bash
# Установка вспомогательных библиотек через conda
conda install -c conda-forge mkl-service mkl intel-openmp -y

# Установка PyTorch (официальная сборка под CUDA 12.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
Установка зависимостей Transformers и HuggingFace
code
Bash
pip install transformers huggingface-hub accelerate datasets evaluate onnxruntime diskcache
Настройка путей (чтобы PLAPT видел GPU, а GNINA не ломалась)
code
Bash
# Принудительно привязываем пути к библиотекам внутри окружения
conda env config vars set LD_LIBRARY_PATH=$CONDA_PREFIX/lib:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# Переактивируем среду, чтобы изменения вступили в силу
conda deactivate
conda activate dock-bench-v2
Предварительная загрузка весов (Критически важно для Slurm!)
Поскольку вычислительные узлы часто не имеют доступа к интернету, нужно один раз запустить PLAPT на логин-ноде, чтобы он скачал модели в кэш.
code
Bash
# Запустите тестовую команду. Она скачает ~2-3 Гб моделей.
python plapt_cli.py -t "SEQUENCE" -m "C1=CC=C(C=C1)C(=O)O"
