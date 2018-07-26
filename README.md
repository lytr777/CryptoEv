# CryptoEv

## Подготовка
Установить numpy
```
pip install numpy
pip install mpi4py (для MPI)
```
Распаковать и собрать SAT-solver'ы.
```
./untar_ling.sh
./untar_rokk.sh
```
P.S. Скрипты запускать из корневой директории проекта!

## Запуск
```
python2.7 main.py id [-cp file/path] [-v 0] [-d file/path]
```

Обязательные аргументы:
* id – суффикс для файлов логов (будет создан файл по следующему пути: ./out/new_log_%id)

Дополнительные аргументы:
* -cp file/path – путь к файлу конфигурации (по умолчанию ./configurations/base.json)
* -v 0 - [0-3] подробность логов отладки (verbosity)
* -d file/path – путь к файлу логов для отладки (по умолчанию пишутся в stdout)

## MPI Запуск
```
mpiexec -n node_count python2.7 mpi_main.py id [-cp file/path]
```
* node_count – число узлов, выделенных для рассчета

## Конфигурация
### Общие параметры
* **algorithm** – Метаэвристический алгоритм
  - *ev* – Эволюционный алгоритм
  - *ts* – Поиск с запретами
### Параметры алгоритма
* **s** – начальная мощность декомпозиционного множества
* **comparator** – способ сравнения декомпозиционных множеств
  - *max_min* – минимальное по значению, наибольшее по числу переменных
* **minimization_function** – оценочная функция
  - *gad* – Guess-and-Determine
  - *ibs* – Inverse Backdoor Sets (подсчет значения с помощью Worker's)
  - *pool_ibs* – Inverse Backdoor Sets (подсчет значения с помощью Pool)
* **mutation_function** – функция мутации
  - *uniform* – равномерная мутация
* **crossover_function** – функция кросинговера
  - *one-point* – одноточечный кросинговер
  - *two-point* – двухточечный кросинговер
  - *uniform* – равномерный кросинговер
* **stop_condition** – условие остановки
  - *iterable* – по числу итераций
  - *mf_calls* – по числу вызовов оценочной функции
  - *locals* – по числу найденых минимумов с установленным числом стагнаций
  - *mf_value* – при достижении требуемого значения
* **stagnation_limit** – число стагнаций
* **evolution_strategy** – эволюционная стратегия
  - *comma* – (mu, lambda)
  - *plus* – (mu + lambda)
  - *genetic* – генетический алгоритм (m, l, c)
### Параметры оценочной функции
* **crypto_algorithm** – криптографический алгоритм
  - *a5_1* – A5/1
  - *bivium* – Bivium
  - *trivium_64* – Trivium 64
  - *trivium_96* – Trivium 96
  - *e0* – E0
* **threads** – число потоков
* **N** – обьем выборки (учитывается, если не задан adaptive_N)
* **adaptive_N** – адаптивное изменение обьема выборки
  - *function* – изменение с помощью встроенной функции (только для шифра A5/1)
* **solver_wrapper** – SAT-решатель
  - *lingeling* – Lingeling
  - *rokk* – ROKK
* **time_limit** – ограничение по времени на решения одной задачи (только для IBS)
* **corrector** – корректировка временного ограничения (только для IBS)
  - *none* – без корректировки
  - *mass* – по принципу центра масс
  - *max* – выбор максимального

## Пример
```
python2.7 main.py trivium_64 -cp configurations/trivium_64.json
```
Запуск алгоритма для поиска **backdoor** множества для шифра Trivium 64
