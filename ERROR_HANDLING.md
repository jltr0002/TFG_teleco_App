# Error Handling Guide - Antenna Synthesis Tool

Esta guía documenta todos los tipos de errores que puede encontrar la aplicación de síntesis de antenas y cómo solucionarlos.

## Índice

1. [Errores de Validación de Parámetros](#errores-de-validacion-de-parametros)
2. [Errores de Entrada de Usuario](#errores-de-entrada-de-usuario)
3. [Errores de Exportación](#errores-de-exportacion)
4. [Errores de Configuración](#errores-de-configuracion)
5. [Errores de Archivo](#errores-de-archivo)
6. [Errores de Cálculo](#errores-de-calculo)

---

## Errores de Validación de Parámetros

### 1. Parámetros Faltantes

**Error**: `missing_parameter:<nombre_parámetro>`

**Causa**: Un parámetro requerido no fue proporcionado por la interfaz gráfica.

**Solución**:
- Verificar que todos los campos obligatorios están completados
- Reiniciar la aplicación si persiste el problema
- Reportar como bug si ocurre consistentemente

---

### 2. Espaciado de Elementos

**Error**: `d_lambda must be positive and finite.`

**Causa**: El espaciado entre elementos es inválido (≤0, infinito, o NaN).

**Solución**:
- Ingresar un valor positivo y finito para el espaciado de elementos
- Valores típicos: 0.25 - 2.0 λ (longitudes de onda)
- Valor recomendado: 0.5 λ para evitar grating lobes

---

### 3. Número de Elementos

**Errores**:
- `Number of elements must be >= 1.` (Método Uniforme)
- `Number of elements must be >= 2.` (Otros métodos)

**Causa**: Se especificó un número de elementos menor al mínimo requerido.

**Solución**:
- **Uniforme**: Usar al menos 1 elemento
- **Otros métodos**: Usar al menos 2 elementos
- Para mejores resultados en Schelkunoff: usar un número impar

---

### 4. Ángulo del Haz Principal

**Errores**:
- `Main beam angle must be between 0 and pi radians (0 to 180 degrees).`
- `theta0_rad must be between 0 and pi radians.`

**Causa**: El ángulo está fuera del rango válido [0°, 180°].

**Solución**:
- Ingresar un ángulo entre 0° y 180°
- 90° corresponde a radiación perpendicular (broadside)
- 0°/180° corresponden a radiación axial (endfire)

---

### 5. Resolución

**Error**: `resolution must be at least 16.`

**Causa**: La resolución es menor a 16 puntos.

**Solución**:
- Usar al menos 16 puntos para la resolución
- Valores recomendados: 360, 720, 1440 para gráficos suaves
- Mayor resolución = cálculos más lentos pero más precisos

---

### 6. Nivel de Lóbulos Secundarios

**Error**: `sidelobe_level_db must be a finite number.`

**Causa**: El nivel especificado no es un número finito.

**Solución**:
- Ingresar un número finito (típicamente 10-60 dB)
- Valores típicos: 20-40 dB para aplicaciones generales
- Mayor valor dB = menor nivel de lóbulos secundarios

---

## Errores de Entrada de Usuario

### 1. Análisis de Nulos

**Error**: `Could not parse 'null_angles'`

**Causa**: Las posiciones de nulos no se pudieron interpretar.

**Solución**:
- Usar formato de lista separada por comas: "30, 60, 120"
- Verificar que todos los valores son números válidos
- Los ángulos deben estar en el rango válido [0°, 180°]

**Ejemplo correcto**:
```
30, 60, 90, 120
```

---

### 2. Posiciones de Nulos Vacías

**Error**: `Null positions cannot be empty.`

**Causa**: No se especificaron posiciones de nulos en el método Schelkunoff.

**Solución**:
- Especificar al menos una posición de nulo
- Ejemplo: "60" para un nulo en 60°
- Múltiples nulos: "45, 90, 135"

---

### 3. Ángulos de Haz (Fourier)

**Errores**:
- `Could not parse beam angles for beam <n>`
- `Invalid angle found in pair (...). All angles must be between 0 and 180 degrees.`
- `For beam #<n>, the start angle (...) must be strictly less than the end angle (...).`

**Causa**: Los ángulos del haz están mal formateados o son inválidos.

**Solución**:
- **1 haz**: "inicio, fin" → Ejemplo: "60, 120"
- **2 haces**: "inicio1, fin1, inicio2, fin2" → Ejemplo: "30, 60, 120, 150"
- **3 haces**: "inicio1, fin1, inicio2, fin2, inicio3, fin3"
- Todos los ángulos deben estar entre 0° y 180°
- El ángulo de inicio debe ser menor que el de fin

---

### 4. Número de Haces

**Error**: `For the selected <n> beam(s), exactly <m> angles are required...`

**Causa**: El número de ángulos no coincide con el número de haces seleccionado.

**Solución**:
- **1 haz**: 2 ángulos (inicio, fin)
- **2 haces**: 4 ángulos (inicio1, fin1, inicio2, fin2)
- **3 haces**: 6 ángulos (inicio1, fin1, inicio2, fin2, inicio3, fin3)

---

### 5. Forma de Haz

**Error**: `Unknown beam shape: '<forma>'`

**Causa**: Se especificó una forma de haz no soportada.

**Solución**:
- Usar solo formas soportadas:
  - `rectangular` - Patrón rectangular
  - `triangular` - Patrón triangular

---

### 6. Expresiones Matemáticas

**Errores**:
- `Invalid expression: <expresión>`
- `Invalid characters in expression: <expresión>`

**Causa**: Expresión matemática inválida en campos de entrada.

**Solución**:
- Usar solo números, operadores básicos (+, -, *, /, ^), paréntesis
- Constantes permitidas: `pi`, `e`
- Funciones permitidas: `sin`, `cos`, `tan`, `sqrt`, `log`, `exp`
- Evitar caracteres especiales o funciones no soportadas

**Ejemplos válidos**:
```
pi/2
90.0
sin(pi/4)
2*pi/3
```

---

## Errores de Exportación

### 1. Sin Resultados para Exportar

**Error**: `No results available to export`

**Causa**: Se intentó exportar antes de ejecutar un cálculo.

**Solución**:
- Ejecutar el cálculo primero usando el botón "Calcular"
- Verificar que el cálculo se completó exitosamente
- Luego proceder con la exportación

---

### 2. Datos de Factor de Array No Disponibles

**Error**: `Array factor data not available in results`

**Causa**: Los datos específicos del factor de array no están presentes.

**Solución**:
- Recalcular usando un método que genere factor de array
- Verificar que el cálculo se completó sin errores
- Reportar como bug si persiste

---

### 3. Widget de Gráficos No Disponible

**Error**: `Plotting widget not available`

**Causa**: Error interno en el sistema de gráficos.

**Solución**:
- Reiniciar la aplicación
- Verificar que matplotlib esté instalado correctamente
- Actualizar dependencias si es necesario

---

## Errores de Configuración

### 1. Archivo de Configuración

**Warning**: `Could not load config file (...). Using defaults.`

**Causa**: 
- Archivo de configuración corrupto o inaccesible
- Permisos insuficientes
- Formato JSON inválido

**Solución**:
- Eliminar el archivo de configuración para regenerarlo
- Verificar permisos de escritura en el directorio de configuración
- Restaurar configuración desde Preferencias → Restablecer

---

### 2. Permisos de Archivo

**Error**: `PermissionError` o `OSError`

**Causa**: Permisos insuficientes para leer/escribir archivos.

**Solución**:
- Ejecutar la aplicación con permisos adecuados
- Verificar permisos de escritura en directorios de configuración
- Cambiar ubicación de archivos de configuración si es necesario

---

## Errores de Archivo

### 1. Archivo No Encontrado

**Error**: `File <filename> not found`

**Causa**: Archivo especificado no existe en la ubicación indicada.

**Solución**:
- Verificar que el archivo existe en la ruta especificada
- Usar el botón "Examinar" para seleccionar archivos
- Verificar permisos de lectura del archivo

---

### 2. Formato JSON Inválido

**Error**: `Invalid JSON format in <filename>`

**Causa**: Archivo JSON corrupto o con sintaxis incorrecta.

**Solución**:
- Verificar sintaxis JSON usando un validador online
- Restaurar desde respaldo si está disponible
- Regenerar el archivo si es de configuración

---

### 3. Estructura de Datos

**Error**: `'element_excitations' not found in JSON data`

**Causa**: Estructura de datos incorrecta en archivo JSON.

**Solución**:
- Verificar que el archivo contiene las claves requeridas
- Usar archivos generados por la propia aplicación
- Consultar documentación de formato de archivos

---

## Errores de Cálculo

### 1. Normalización

**Error**: `Unknown normalization method: '<método>'`

**Causa**: Método de normalización no reconocido.

**Solución**:
- Usar métodos de normalización soportados
- Verificar configuración de normalización
- Reportar como bug si se usa interfaz estándar

---

### 2. Elemento de Referencia

**Error**: `Reference element <idx> has zero magnitude, cannot normalize`

**Causa**: El elemento de referencia tiene magnitud cero.

**Solución**:
- Seleccionar un elemento diferente como referencia
- Verificar que los resultados del cálculo son válidos
- Recalcular si los datos parecen incorrectos

---

### 3. Errores de Plotting

**Error**: Excepciones genéricas en sistema de gráficos

**Causa**: Problemas con matplotlib o datos de entrada inválidos.

**Solución**:
- Reinstalar matplotlib: `pip install --upgrade matplotlib`
- Verificar que los datos de entrada son válidos
- Reiniciar la aplicación
- Reportar con datos específicos si persiste

---

## Soluciones Generales

### Pasos de Diagnóstico

1. **Verificar Entrada**:
   - Todos los campos requeridos completados
   - Valores dentro de rangos válidos
   - Formato correcto de datos

2. **Reiniciar Aplicación**:
   - Cerrar completamente la aplicación
   - Reiniciar para limpiar estado

3. **Verificar Dependencias**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. **Restablecer Configuración**:
   - Eliminar archivos de configuración
   - Permitir regeneración automática

5. **Reportar Bugs**:
   - Incluir mensaje de error exacto
   - Pasos para reproducir
   - Configuración del sistema

### Valores Recomendados por Defecto

- **Espaciado de elementos**: 0.5 λ
- **Resolución**: 360 puntos
- **Ángulo principal**: 90° (broadside)
- **Nivel de lóbulos secundarios**: 30 dB
- **Número de elementos**: 10-20 para pruebas iniciales

### Contacto y Soporte

Para errores no documentados o problemas persistentes:
- Consultar archivo CLAUDE.md para información de desarrollo
- Reportar issues con detalles completos
- Incluir logs de error cuando sea posible