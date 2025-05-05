# Пакет mse-task-generators 
## Установка пакета
```
pip install mse-task-generators
```
При установке пакета устанавливаются и зависимости, необходимые для корректной работы команд.

## Утилиты для пользования генераторами
Нижеперечисленные утилиты должны принимать различные аргументы, информация о которых доступна при добавлении флага **--help\-h**

### Генератор задач с циклом
```
generators-cycle-generator flag1 <arg1>, flag2 <arg2> ...
```

### Генератор задач с утечкой памяти
```
generators-leak-generator flag1 <arg1>, flag2 <arg2> ...
```

### Генератор задач на профилирование 
```
generators-profiling1 flag1 <arg1>, flag2 <arg2> ...
```



## Импортирование функций в программу на Python

```
from generators.leak_generator import LeaksGenerator
from generators.cycle_generator import CCodeGenerator
from generators.cycle_generator import upload_file_to_yadisk
from generators.profiling1 import TaskFindingSlowFunctionGenerator
from generators.profiling1 import TaskFindingSlowFuncInFuncGenerator
```