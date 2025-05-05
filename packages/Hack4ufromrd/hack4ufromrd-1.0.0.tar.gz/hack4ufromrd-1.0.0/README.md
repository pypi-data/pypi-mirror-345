# HACK4U Academy Course Library

Una biblioteca Python para consultar cursos de la academia Hack4U.

## Cursos disponibles:

- Introduccion a Linux [15 horas]
- Personalizacion de Linux [3 horas]
- Introduccion al Hacking [53 horas]

## Instalacion

Instala el paquete usando 'pip3':

```python
pip3 install Hack4U
```

## Uso basico

### Listar todos los cursos

```python
from hack4u import list_courses

for course in list_courses():
    print(course)
```

### Obtener en curso por nombre

```python
from hack4u import search_course_by_name

course = source_course_by_name("Introduccion a Linux")
print(course)
```

### Calcular duracion total de los cursos

```python3
from hack4u.utils import total_duration

print(f"Duracioon total: {total_duration()} horas")
```
