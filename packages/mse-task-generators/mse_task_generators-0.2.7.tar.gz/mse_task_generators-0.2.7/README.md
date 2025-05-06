## Оглавление  
- [Инструкция по развертыванию проекта](#Инструкция-по-развертыванию-проекта)  
- [Функционал проекта](#Функционал-проекта)  
- [CodeRunner Moodle](#coderunner-moodle)  

## Инструкция по развертыванию проекта

### Требования к системе
- **ОС**: Linux (рекомендуется Ubuntu 20.04 LTS или выше)
- **Python**: версия 3.8 или выше
- **Компилятор**: GCC (GNU Compiler Collection)
- **Инструменты отладки и профилирования**:
  - Valgrind
  - GDB (GNU Debugger)
  - Gprof (GNU Profiler)

---

### 1. Установка зависимостей
#### Установка Python, PIP и venv
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### Установка GCC, Valgrind, GDB, Gprof
```bash
sudo apt install gcc valgrind gdb binutils
```

#### Проверка версий
```bash
python3 --version
pip3 --version     
python3 -m venv --help 
gcc --version
valgrind --version
gdb --version
gprof --version
```

---

### 2. Клонирование репозитория
```bash
git clone https://github.com/moevm/mse1h2025-perf.git
cd mse1h2025-perf
```

---

### 3. Установка Python-зависимостей
```bash
python3 -m venv venv  
source venv/bin/activate  
(venv) pip install -r requirements.txt
```

---

## Функционал проекта
### Примеры использования генераторов задач
Проект поддерживает 3 генератора задач. Ниже приведены примеры их запуска.

#### Генератор 1:
#### Создание задач на профилирование
```bash
python3 -m generators.profiling1 1 init -o test.out
```
#### Проверка задач на профилирование
```bash
python3 -m generators.profiling1 1 check -b test.out -a f1
```
#### Параметры:
- `Первый параметр`: тип задачи (1, 2)
- `Второй параметр`: создание задачи или проверка ответа (init, check)
- С полным списком параметров можно ознакомиться в документации к генератору - [Документация](https://github.com/moevm/mse1h2025-perf/blob/main/generators/profiling1/README.md)

#### Генератор 2:
#### Создание задач на утечку памяти
```bash
python3 -m generators.leak_generator -m 1
```
#### Проверка задач на утечку памяти
```bash
python3 -m generators.leak_generator -m 2
```
#### Параметры:
- `--mode, -m`: создание задачи иили проверка ответа (1, 2)
- С полным списком параметров можно ознакомиться в документации к генератору - [Документация](https://github.com/moevm/mse1h2025-perf/blob/main/generators/leak_generator/README.md)

#### Генератор 3:
#### Создание задач на отладку
```bash
python3 -m generators.cycle_generator -m 1
```
#### Проверка задач на отладку
```bash
python3 -m generators.cycle_generator -m 2
```
#### Параметры:
- `--mode, -m`: создание задачи или проверка ответа (1, 2)
- С полным списком параметров можно ознакомиться в документации к генератору - [Документация](https://github.com/moevm/mse1h2025-perf/blob/main/generators/cycle_generator/README.md)
---


## Пакет mse-task-generators 
### Установка пакета
```
pip install mse-task-generators
```
При установке пакета устанавливаются и зависимости, необходимые для корректной работы команд.

### Утилиты для пользования генераторами
Нижеперечисленные утилиты должны принимать различные аргументы, информация о которых доступна при добавлении флага **--help\-h**

#### Генератор задач с циклом
```
generators-cycle-generator flag1 <arg1>, flag2 <arg2> ...
```

#### Генератор задач с утечкой памяти
```
generators-leak-generator flag1 <arg1>, flag2 <arg2> ...
```

#### Генератор задач на профилирование 
```
generators-profiling1 flag1 <arg1>, flag2 <arg2> ...
```



### Импортирование функций в программу на Python

```
from generators.leak_generator import LeaksGenerator
from generators.cycle_generator import CCodeGenerator
from generators.cycle_generator import upload_file_to_yadisk
from generators.profiling1 import TaskFindingSlowFunctionGenerator
from generators.profiling1 import TaskFindingSlowFuncInFuncGenerator
```



