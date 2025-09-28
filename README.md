# Laboratorio 7 - Teoria de la Computacion

## Autores
- 22046 - Nelson Escalante
- 23384 - Eliazar Canastuj
- 23601 – Diego Ramirez 

## Video de los programas.
[Ver en video](https://uvggt-my.sharepoint.com/:v:/g/personal/ram23601_uvg_edu_gt/EeZ_g5kxSPhCsxzXXYCRbpcB8kXc2Mankb7bARTWQF-B7Q?e=CA4G8b&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D)
[Video del problema 3]()


## Requisitos

- Python 3.8+
- Codificación de archivos: **UTF-8** (especialmente para el carácter `ε`).

> Archivo principal: `lab7.py`  
> Ejemplos incluidos: `gramatica1.txt`, `gramatica2.txt`

---

## Instalación / Descarga

- Código: `lab7.py`  
- Ejemplos:  
  - `gramatica1.txt`  
  - `gramatica2.txt`

Guarda el script y tus archivos de gramática en la misma carpeta (o pasa rutas absolutas).

---

## Uso

```bash
python lab7.py gramatica1.txt [gramatica2.txt ...]
```

El programa:

1. Lee y **valida** cada línea.
2. Imprime:
   - Símbolos **anulables** por iteración.
   - Para cada producción, las **posiciones anulables** del cuerpo y cada nueva alternativa generada.
3. Quita **todas** las producciones-ε (mantiene `S -> ε` si `S` es anulable).
4. Escribe la gramática resultante en `*_sin_epsilon.txt`.

---

## Formato de entrada (archivos de gramática)

- Una producción por línea:
  - Flecha `->` o `→`
  - Alternativas separadas por `|`
  - `ε` como **única** alternativa (no se permite mezclar, p. ej., `aε`)
- **No terminales**: letras **mayúsculas** (un carácter): `A..Z`  
- **Terminales**: letras **minúsculas** o **dígitos**: `a..z`, `0..9`  
- Sin espacios **dentro** de los cuerpos (la concatenación va pegada).

**Ejemplo válido**
```
S -> 0A0 | 1B1 | BB
A -> C
B -> S | A
C -> S | ε
```

**Ejemplo con error (se detiene)**
```
S - > a    # espacios en la flecha
A -> aε    # mezcla ε con otros símbolos
```

**Tu gramática del ejemplo**
```
S -> ADA | aC | Bd
A -> a | ε
B -> b | ε
C -> AB | c
D -> d
```

> Consejo: si usas la flecha `→`, guarda el archivo en **UTF-8**.

---

## Salida

El programa muestra en consola los **pasos** y genera un archivo por cada entrada:

- `gramatica1_sin_epsilon.txt`
- `gramatica2_sin_epsilon.txt`

---

## Detalles del algoritmo

1. **Símbolos anulables (Nullable)**
   - Si `A -> ε`, entonces `A` es anulable.
   - Si `A -> X1…Xk` y **todos** `Xi` son no terminales anulables, entonces `A` es anulable.
   - Se itera hasta alcanzar **punto fijo**.

2. **Generación de combinaciones (2^m)**
   - Para cada `A -> X1…Xn`, marca las **posiciones anulables** del cuerpo.
   - Genera todas las alternativas resultantes de **eliminar** cualquier subconjunto **no vacío** de esas posiciones.
   - **Nunca** produce `ε` salvo que `A` sea el **símbolo inicial** y éste sea anulable.

3. **Limpieza**
   - Se eliminan las producciones `-> ε` restantes (excepto `S -> ε` si corresponde).
   - Se **deduplican** alternativas.
   - Si algún no terminal queda **sin producciones**, no se imprime.

---

## Validación de producciones

Se utiliza la siguiente expresión regular (acepta `->` o `→`, alternativas con `|`, y `ε`):

```
^\s*([A-Z])\s*(?:->|→)\s*(?:ε|[A-Za-z0-9]+)(?:\s*\|\s*(?:ε|[A-Za-z0-9]+))*\s*$
```

Reglas adicionales:
- `ε` debe ir **solo** (no `aε`, `εb`, etc.).
- La concatenación no lleva espacios: usar `aB`, `0A0`, `ABd`, etc.

---

## Estructura del proyecto

```
.
├── lab7.py        # Script principal
├── gramatica1.txt            # Ejemplo 1
├── gramatica2.txt            # Ejemplo 2
├── gramatica1_sin_epsilon.txt (se genera al correr)
└── gramatica2_sin_epsilon.txt (se genera al correr)
```

---

## Errores comunes y soluciones

- **“Producción mal escrita”**  
  Revisa flecha (`->` o `→`), uso de `|`, que `ε` no esté mezclado con otros símbolos, y que no haya espacios dentro de los cuerpos.
- **Caracteres especiales no reconocidos (ε, →)**  
  Guarda el archivo en **UTF-8**.
- **Símbolo no terminal sin producciones**  
  El script omite no terminales que queden sin alternativas; verifica tu gramática si esperabas reglas para ese símbolo.

