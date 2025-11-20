# Docking Benchmark Suite

Воспроизводимый бенчмарк для сравнения методов молекулярного докинга.

## Методы докинга

- **QVina** - Быстрая версия AutoDock Vina
- **AutoDock Vina** - Классический метод докинга
- **Boltz-2** - Нейросетевой метод с предсказанием аффинности
- **DynamicBind** - Гибкий докинг с динамическим белком
- **Uni-Mol** - Универсальная молекулярная модель
- **Interformer** - Трансформер для взаимодействий
- **Gnina 1.3** - Vina с CNN scoring
- **PLAPT** - Protein-Ligand Affinity Prediction Transformer

## Установка

### Через pip

```bash
pip install -e .
```

### Через conda

```bash
conda env create -f environment.yml
conda activate docking-benchmark
```

## Быстрый старт

1. Подготовьте данные:
   - Поместите PDB файлы белков в `data/input/proteins/`
   - Поместите CSV файлы с SMILES лигандов в `data/input/ligands/`
   
   Формат CSV файла:
   - Обязательная колонка: `smiles` (или `SMILES`, `Smiles`, `canonical_smiles`, и т.д.) - SMILES строки
   - Опциональная колонка: `ligand_id` (или `id`, `ligand`, `name`) - идентификаторы лигандов

2. Настройте конфигурацию в `run_benchmark.sh`:
   ```bash
   # Укажите пути к бинарникам методов
   QVINA_BINARY="/path/to/qvina02"
   VINA_BINARY="/path/to/vina"
   
   # Настройте conda окружения
   PREPROCESSING_ENV="meeko"  # Окружение для подготовки файлов
   BOLTZ_ENV="boltz-env"      # Окружение для Boltz-2
   
   # Выберите методы для запуска
   METHODS=("qvina" "vina" "boltz2")
   ```
   
   Или настройте в `config/default_config.yaml` и `config/methods_config.yaml`

3. Запустите бенчмарк:
   ```bash
   bash scripts/run_benchmark.sh
   ```

## Структура проекта

```
docking-benchmark/
├── src/docking_benchmark/    # Основной код
├── config/                   # Конфигурационные файлы
├── scripts/                  # Вспомогательные скрипты
├── tests/                    # Тесты
├── data/                     # Данные (не в git)
└── docs/                     # Документация
```

## Метрики

Бенчмарк рассчитывает следующие метрики:

- **RMSD** - Root Mean Square Deviation (лиганд, карман, белок)
- **Время выполнения** - Время докинга для каждого метода
- **Аффинность** - Предсказанная аффинность связывания (если доступна)
- **Clash score** - Оценка столкновений атомов

## Результаты

Результаты сохраняются в:
- `data/results/raw/` - Сырые результаты докинга
- `data/results/metrics/` - Рассчитанные метрики (CSV)
- `data/results/reports/` - HTML отчеты с визуализацией

## Документация

Подробная документация доступна в папке `docs/`:
- [Установка](docs/installation.md)
- [Использование](docs/usage.md)
- [Описание методов](docs/methods.md)
- [Метрики](docs/metrics.md)

## Лицензия

MIT License

## Цитирование

Если вы используете этот бенчмарк в своих исследованиях, пожалуйста, цитируйте соответствующие статьи для каждого метода докинга.

