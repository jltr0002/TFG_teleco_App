# Herramienta de Síntesis de Antenas

Una aplicación GUI integral en Python para la síntesis de arreglos de antenas utilizando varios métodos matemáticos. Esta herramienta proporciona una interfaz gráfica intuitiva para calcular y visualizar patrones de arreglos de antenas con retroalimentación en tiempo real y capacidades avanzadas de graficado.

## Descripción del Proyecto

La Herramienta de Síntesis de Antenas está diseñada para ingenieros, investigadores y estudiantes que trabajan con diseño de arreglos de antenas. Implementa varios métodos de síntesis probados para calcular excitaciones óptimas de elementos para patrones de radiación deseados.

### Características Principales

- **Múltiples Métodos de Síntesis**: Síntesis de arreglos Schelkunoff, Fourier, Dolph-Chebyshev y Uniforme
- **GUI Interactiva**: Construida con PySide6 para una experiencia de usuario responsive
- **Visualización en Tiempo Real**: Graficado en vivo de factores de arreglo en coordenadas rectangulares y polares
- **Análisis de Elementos**: Visualización de excitaciones de elementos y geometría del arreglo
- **Capacidades de Exportación**: Guardar resultados y gráficos para documentación y análisis
- **Internacionalización**: Infraestructura de soporte multiidioma
- **Computación con Hilos**: Cálculos no bloqueantes con retroalimentación de progreso

## Métodos de Síntesis

### 1. Método de Schelkunoff
- **Propósito**: Síntesis basada en polinomios para colocación precisa de nulos
- **Mejor para**: Aplicaciones que requieren posiciones específicas de nulos en el patrón de radiación
- **Entrada**: Número de elementos, espaciado de elementos, ángulos de nulos
- **Salida**: Excitaciones de elementos que colocan nulos en ángulos especificados

### 2. Síntesis de Fourier
- **Propósito**: Síntesis de arreglo lineal desde patrones de factor de arreglo deseados
- **Mejor para**: Crear haces conformados con regiones angulares definidas
- **Entrada**: Forma del haz (rectangular/triangular), ángulos del haz, número de elementos
- **Salida**: Excitaciones de elementos para patrón de haz deseado

### 3. Síntesis Dolph-Chebyshev
- **Propósito**: Síntesis óptima para control uniforme de lóbulos laterales
- **Mejor para**: Aplicaciones que requieren niveles constantes de lóbulos laterales
- **Entrada**: Número de elementos, nivel de lóbulos laterales, dirección del haz principal
- **Salida**: Excitaciones con ancho de haz mínimo para nivel dado de lóbulos laterales

## Instalación y Configuración
### Instalación Rápida

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd Antennas_claude
   ```

2. **Crear y activar entorno virtual**
   ```bash
   # Linux/macOS
   python -m venv .venv
   source .venv/bin/activate
   
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   python main.py
   ```

### Dependencias Principales
- **PySide6** (≥6.2.0): Framework GUI moderno basado en Qt
- **NumPy** (≥1.21.0): Fundamento de computación numérica
- **Matplotlib** (≥3.5.0): Graficado avanzado y visualización
- **SciPy** (≥1.7.0): Utilidades de computación científica
- **mplcursors** (≥0.6): Cursores interactivos de gráficos
- **PyInstaller** (≥6.15.0): Generación de ejecutables

### Solución de Problemas de Instalación
```bash
# Actualizar pip primero
python -m pip install --upgrade pip

# Instalación con salida detallada para depuración
pip install -r requirements.txt -v

# Reinstalar forzadamente si hay corrupción
pip install --force-reinstall -r requirements.txt

# Instalar desde archivos wheel si falla la compilación
pip install --only-binary=all -r requirements.txt
```

## Creación de Ejecutable (.exe)

### Usando PyInstaller

#### Comando Básico
```bash
pyinstaller --onefile --windowed main.py
```

#### Comando Recomendado (con optimizaciones)
```bash
pyinstaller --noconfirm --onefile --windowed --name="AntennasSynthesis" --add-data "gui/plots/element_placement;gui/plots/element_placement" --add-data "config;config" main.py
```

#### Comando Avanzado (optimizado para tamaño)
```bash
pyinstaller --onefile --windowed \
    --name="AntennasSynthesis" \
    --exclude-module=PIL \
    --exclude-module=tkinter \
    --exclude-module=test \
    --exclude-module=unittest \
    --exclude-module=distutils \
    --exclude-module=setuptools \
    main.py
```

#### Comandos Específicos por Plataforma

**Windows:**
```cmd
pyinstaller --noconfirm --onefile --windowed --name="AntennasSynthesis" --add-data "gui/plots/element_placement;gui/plots/element_placement" --add-data "config;config" main.py
```

**macOS:**
```bash
pyinstaller --onefile --windowed --name="AntennasSynthesis" --icon=icon.icns main.py
```

**Linux:**
```bash
pyinstaller --onefile --windowed --name="AntennasSynthesis" main.py
```

### Parámetros de PyInstaller Explicados

| Parámetro | Descripción |
|-----------|-------------|
| `--onefile` | Crear un único archivo ejecutable |
| `--windowed` | Ocultar ventana de consola (solo GUI) |
| `--name` | Especificar nombre del ejecutable |
| `--icon` | Establecer icono personalizado de aplicación |
| `--exclude-module` | Excluir módulos innecesarios |
| `--hidden-import` | Incluir módulos no detectados automáticamente |
| `--add-data` | Incluir archivos de datos adicionales |

### Estructura de Salida de Construcción
```
/
├── main.py                         # Main application entry point
├── requirements.txt                # Project dependencies
├── BUILD.md                        # Build instructions and setup guide
├── ERROR_HANDLING.md               # Error handling documentation
├── README.md                       # Project documentation
├── config/                         # Configuration management
│   ├── __init__.py
│   ├── README.md                   # Configuration documentation
│   ├── config.json                 # Application configuration
│   ├── config_2.json               # Alternative configuration
│   ├── constants.py                # Application constants
│   └── settings.py                 # Settings management
├── methods/                        # Synthesis method implementations
│   ├── __init__.py
│   ├── schelkunoff.py             # Schelkunoff polynomial method
│   ├── fourier.py                 # Fourier synthesis method
│   ├── dolph_chebyshev.py         # Dolph-Chebyshev synthesis method
│   ├── synthesis.py               # Base synthesis class
├── gui/                           # GUI components
│   ├── __init__.py
│   ├── main_window.py             # Main application window
│   ├── plotting_widget.py         # Plotting and visualization
│   ├── detachable_plot_window.py  # Detachable plot window
│   ├── preferences_dialog.py      # User preferences dialog
│   ├── controllers/               # GUI controllers (empty)
│   └── plots/                     # Modular plotting system
│       ├── __init__.py
│       ├── base_plot.py           # Base plotting widget
│       ├── rectangular_plot.py    # Rectangular plot implementation
│       └── element_placement/     # Element placement diagrams
│           ├── even.png           # Even element placement diagram
│           ├── even.svg           # Even element placement (SVG)
│           ├── odd.png            # Odd element placement diagram
│           ├── odd.svg            # Odd element placement (SVG)
│           ├── unilatera.svg      # Unilateral placement (SVG)
│           └── unilateral.png     # Unilateral placement diagram
└── translations/                  # Internationalization support
    ├── __init__.py
    └── translations.py            # Translation system
```

### Ubicación del Ejecutable
- **Windows**: `dist/AntennasSynthesis.exe`
- **macOS**: `dist/AntennasSynthesis`
- **Linux**: `dist/AntennasSynthesis`

### Optimización de Construcción

#### Reducir Tamaño de Archivo
1. **Excluir Módulos Innecesarios**
```bash
--exclude-module=PIL \
--exclude-module=tkinter \
--exclude-module=test \
--exclude-module=unittest
```

2. **Usar Compresión UPX** (opcional)
```bash
# Instalar UPX primero, luego agregar a PyInstaller
--upx-dir=path/to/upx
```

3. **Crear archivo .spec para Control Avanzado**
```bash
# Generar archivo .spec
pyi-makespec --onefile --windowed main.py

# Editar archivo .spec, luego construir
pyinstaller AntennasSynthesis.spec
```

#### Optimización de Rendimiento
1. **Habilitar Optimización de Bytecode**
```bash
pyinstaller --onefile --windowed --optimize=2 main.py
```

2. **Modo Bundle Directory** (inicio más rápido)
```bash
pyinstaller --noconfirm --onefile --windowed --name="AntennasSynthesis" --add-data "gui/plots/element_placement;gui/plots/element_placement" --add-data "config;config" main.py
```

### Solución de Problemas de Construcción

#### Módulos Faltantes
**Error**: `ModuleNotFoundError` durante ejecución
**Solución**:
```bash
pyinstaller --hidden-import=nombre_modulo_faltante main.py
```

#### Archivo Muy Grande
**Problema**: Ejecutable superior a 200MB
**Soluciones**:
- Usar `--exclude-module` para dependencias innecesarias
- Considerar `--onedir` en lugar de `--onefile`
- Usar entorno virtual con dependencias mínimas

#### Inicio Lento
**Problema**: Tiempo de inicio largo para ejecutable
**Soluciones**:
- Usar modo `--onedir` en lugar de `--onefile`
- Optimizar importaciones en main.py
- Considerar carga perezosa de módulos pesados

#### Errores de Permisos
**Error**: No se puede escribir en directorio dist/
**Soluciones**:
```bash
# Windows: Ejecutar como administrador
# Linux/macOS: Verificar permisos de directorio
chmod 755 .
sudo pyinstaller ... # si es necesario
```

### Problemas Específicos por Plataforma

#### Windows
- **Advertencia de Antivirus**: Agregar ejecutable a lista blanca
- **Problemas de DLL**: Asegurar que Visual C++ Redistributables estén instalados
- **Longitud de Ruta**: Usar rutas de construcción más cortas si ocurren errores

#### macOS
- **Codesigning**: Puede necesitar firmar ejecutable para distribución
- **Gatekeeper**: Los usuarios pueden necesitar permitir aplicaciones sin firmar
- **Permisos**: Verificar permisos de Terminal en Seguridad y Privacidad

#### Linux
- **Dependencias**: Asegurar que las librerías del sistema estén disponibles
- **Display**: Establecer variable DISPLAY si se ejecuta remotamente
- **Permisos**: Hacer ejecutable con `chmod +x`

### Lista de Verificación de Construcción

**Antes de construir:**
- [ ] Todas las dependencias instaladas
- [ ] La aplicación se ejecuta correctamente desde código fuente
- [ ] Entorno virtual activado
- [ ] Espacio en disco suficiente disponible

**Después de construir:**
- [ ] Ejecutable creado exitosamente
- [ ] Tamaño de archivo razonable (< 300MB típicamente)
- [ ] Se ejecuta en sistema objetivo
- [ ] Todas las características funcionales
- [ ] Sin dependencias faltantes

## Ejemplos de Uso

### Flujo de Trabajo Básico

1. **Seleccionar Método**: Elegir método de síntesis del menú desplegable
2. **Configurar Parámetros**: Establecer número de elementos, espaciado y parámetros específicos del método
3. **Calcular**: Hacer clic en "Calcular" para ejecutar síntesis
4. **Visualizar**: Examinar gráficos de factor de arreglo y excitación de elementos
5. **Exportar**: Guardar resultados para documentación

### Configuraciones de Ejemplo

**Arreglo Uniforme (Broadside)**
- Elementos: 16
- Espaciado: 0.5λ  
- Ángulo del haz: 90°

**Colocación de Nulos Schelkunoff**
- Elementos: 15 (impar recomendado)
- Ángulos de nulos: "45, 135" (grados)
- Espaciado: 0.5λ

**Dolph-Chebyshev Lóbulos Laterales Bajos**
- Elementos: 20
- Nivel de lóbulos laterales: 30 dB
- Dirección del haz: 90°

## Manejo de Errores

La aplicación incluye un sistema integral de manejo de errores diseñado para proporcionar retroalimentación clara y soluciones específicas para cada tipo de problema.

### Errores de Validación de Parámetros

#### Espaciado de Elementos
**Error**: `d_lambda must be positive and finite.`
**Causa**: El espaciado entre elementos es inválido (≤0, infinito, o NaN)
**Solución**: 
- Ingresar un valor positivo y finito para el espaciado de elementos
- Valores típicos: 0.25 - 2.0 λ (longitudes de onda)
- Valor recomendado: 0.5 λ para evitar lóbulos de rejilla

#### Número de Elementos
**Errores**:
- `Number of elements must be >= 2.` (Otros métodos)

**Soluciones**:
- **Uniforme**: Usar al menos 1 elemento
- **Otros métodos**: Usar al menos 2 elementos
- Para mejores resultados en Schelkunoff: usar un número impar

#### Ángulo del Haz Principal
**Errores**:
- `Main beam angle must be between 0 and pi radians (0 to 180 degrees).`
- `theta0_rad must be between 0 and pi radians.`

**Soluciones**:
- Ingresar un ángulo entre 0° y 180°
- 90° corresponde a radiación perpendicular (broadside)
- 0°/180° corresponden a radiación axial (endfire)

#### Resolución
**Error**: `resolution must be at least 16.`
**Soluciones**:
- Usar al menos 16 puntos para la resolución
- Valores recomendados: 360, 720, 1440 para gráficos suaves
- Mayor resolución = cálculos más lentos pero más precisos

#### Nivel de Lóbulos Secundarios
**Error**: `sidelobe_level_db must be a finite number.`
**Soluciones**:
- Ingresar un número finito (típicamente 10-60 dB)
- Valores típicos: 20-40 dB para aplicaciones generales
- Mayor valor dB = menor nivel de lóbulos secundarios

### Errores de Entrada de Usuario

#### Análisis de Nulos (Método Schelkunoff)
**Error**: `Could not parse 'null_angles'`
**Soluciones**:
- Usar formato de lista separada por comas: "30, 60, 120"
- Verificar que todos los valores son números válidos
- Los ángulos deben estar en el rango válido [0°, 180°]

**Ejemplo correcto**: `30, 60, 90, 120`

#### Posiciones de Nulos Vacías
**Error**: `Null positions cannot be empty.`
**Soluciones**:
- Especificar al menos una posición de nulo
- Ejemplo: "60" para un nulo en 60°
- Múltiples nulos: "45, 90, 135"

#### Ángulos de Haz (Método Fourier)
**Errores**:
- `Could not parse beam angles for beam <n>`
- `Invalid angle found in pair (...). All angles must be between 0 and 180 degrees.`
- `For beam #<n>, the start angle (...) must be strictly less than the end angle (...).`

**Soluciones**:
- **1 haz**: "inicio, fin" → Ejemplo: "60, 120"
- **2 haces**: "inicio1, fin1, inicio2, fin2" → Ejemplo: "30, 60, 120, 150"
- **3 haces**: "inicio1, fin1, inicio2, fin2, inicio3, fin3"
- Todos los ángulos deben estar entre 0° y 180°
- El ángulo de inicio debe ser menor que el de fin

#### Número de Haces
**Error**: `For the selected <n> beam(s), exactly <m> angles are required...`
**Soluciones**:
- **1 haz**: 2 ángulos (inicio, fin)
- **2 haces**: 4 ángulos (inicio1, fin1, inicio2, fin2)
- **3 haces**: 6 ángulos (inicio1, fin1, inicio2, fin2, inicio3, fin3)

#### Forma de Haz
**Error**: `Unknown beam shape: '<forma>'`
**Soluciones**:
- Usar solo formas soportadas:
  - `rectangular` - Patrón rectangular
  - `triangular` - Patrón triangular

#### Expresiones Matemáticas
**Errores**:
- `Invalid expression: <expresión>`
- `Invalid characters in expression: <expresión>`

**Soluciones**:
- Usar solo números, operadores básicos (+, -, *, /, ^), paréntesis
- Constantes permitidas: `pi`, `e`
- Funciones permitidas: `sin`, `cos`, `tan`, `sqrt`, `log`, `exp`
- Evitar caracteres especiales o funciones no soportadas

**Ejemplos válidos**: `pi/2`, `90.0`, `sin(pi/4)`, `2*pi/3`

### Errores de Exportación

#### Sin Resultados para Exportar
**Error**: `No results available to export`
**Soluciones**:
- Ejecutar el cálculo primero usando el botón "Calcular"
- Verificar que el cálculo se completó exitosamente
- Luego proceder con la exportación

#### Datos de Factor de Array No Disponibles
**Error**: `Array factor data not available in results`
**Soluciones**:
- Recalcular usando un método que genere factor de array
- Verificar que el cálculo se completó sin errores
- Reportar como error si persiste

#### Widget de Gráficos No Disponible
**Error**: `Plotting widget not available`
**Soluciones**:
- Reiniciar la aplicación
- Verificar que matplotlib esté instalado correctamente
- Actualizar dependencias si es necesario

### Errores de Configuración

#### Archivo de Configuración
**Advertencia**: `Could not load config file (...). Using defaults.`
**Soluciones**:
- Eliminar el archivo de configuración para regenerarlo
- Verificar permisos de escritura en el directorio de configuración
- Restaurar configuración desde Preferencias → Restablecer

#### Permisos de Archivo
**Errores**: `PermissionError` o `OSError`
**Soluciones**:
- Ejecutar la aplicación con permisos adecuados
- Verificar permisos de escritura en directorios de configuración
- Cambiar ubicación de archivos de configuración si es necesario

### Errores de Archivo

#### Archivo No Encontrado
**Error**: `File <filename> not found`
**Soluciones**:
- Verificar que el archivo existe en la ruta especificada
- Usar el botón "Examinar" para seleccionar archivos
- Verificar permisos de lectura del archivo

#### Formato JSON Inválido
**Error**: `Invalid JSON format in <filename>`
**Soluciones**:
- Verificar sintaxis JSON usando un validador online
- Restaurar desde respaldo si está disponible
- Regenerar el archivo si es de configuración

#### Estructura de Datos
**Error**: `'element_excitations' not found in JSON data`
**Soluciones**:
- Verificar que el archivo contiene las claves requeridas
- Usar archivos generados por la propia aplicación
- Consultar documentación de formato de archivos

### Errores de Cálculo

#### Normalización
**Error**: `Unknown normalization method: '<método>'`
**Soluciones**:
- Usar métodos de normalización soportados
- Verificar configuración de normalización
- Reportar como error si se usa interfaz estándar

#### Elemento de Referencia
**Error**: `Reference element <idx> has zero magnitude, cannot normalize`
**Soluciones**:
- Seleccionar un elemento diferente como referencia
- Verificar que los resultados del cálculo son válidos
- Recalcular si los datos parecen incorrectos

#### Errores de Plotting
**Error**: Excepciones genéricas en sistema de gráficos
**Soluciones**:
- Reinstalar matplotlib: `pip install --upgrade matplotlib`
- Verificar que los datos de entrada son válidos
- Reiniciar la aplicación
- Reportar con datos específicos si persiste

### Solución Rápida de Problemas

1. **Verificar Rangos de Entrada**: Verificar que todos los parámetros estén dentro de rangos válidos
2. **Usar Valores por Defecto Recomendados**: Comenzar con valores conocidos como buenos
3. **Reiniciar Aplicación**: Limpiar cualquier problema de estado transitorio
4. **Actualizar Dependencias**: Asegurar que todas las librerías estén actualizadas
5. **Restablecer Configuración**: Eliminar archivos de configuración para restaurar valores por defecto

### Valores Recomendados por Defecto

- **Espaciado de elementos**: 0.5 λ
- **Resolución**: 360 puntos
- **Ángulo principal**: 90° (broadside)
- **Nivel de lóbulos secundarios**: 30 dB
- **Número de elementos**: 10-20 para pruebas iniciales

## Configuración

### Parámetros Globales
- **Precisión**: Control de precisión de cálculos
- **Unidades**: Grados o radianes para entrada de ángulos
- **Resolución**: Número de muestras de ángulo (16-3600)
- **Umbral**: Nivel mínimo de gráfico (dB)

### Configuraciones de Aplicación
Las configuraciones se guardan automáticamente en archivos de configuración JSON. Restablecer a valores por defecto a través del diálogo de Preferencias.

## Fundamentos de Teoría de Arreglos

### Conceptos Fundamentales

**Factor de Arreglo**: La representación matemática del patrón de radiación
```
AF(θ) = Σ(n=0 to N-1) I_n * exp(j * k * d * n * cos(θ))
```

**Parámetros Clave**:
- `I_n`: Excitación compleja del elemento n
- `k`: Número de onda (2π/λ)
- `d`: Espaciado de elementos
- `θ`: Ángulo de observación

### Consideraciones de Diseño

- **Lóbulos de Rejilla**: Evitar manteniendo espaciado ≤ λ/2
- **Control de Lóbulos Laterales**: Compromiso entre ancho de haz y nivel de lóbulos laterales
- **Colocación de Nulos**: Posicionamiento estratégico de nulos para supresión de interferencia
- **Dirección del Haz**: Progresión de fase para control direccional

## Contribuir

Damos la bienvenida a contribuciones. Por favor considere:

1. **Agregar Nuevos Métodos**: Implementar nuevos algoritmos de síntesis
2. **Mejoras de GUI**: Características mejoradas de interfaz de usuario
3. **Documentación**: Comentarios de código y guías de usuario
4. **Pruebas**: Pruebas unitarias y casos de validación
5. **Traducciones**: Soporte de idiomas adicionales

### Directrices de Desarrollo

- Seguir estándares de codificación PEP8
- Usar snake_case para variables y funciones
- Implementar clase base abstracta `SynthesisMethod` para nuevos métodos
- Incluir docstrings comprehensivos
- Agregar manejo apropiado de errores

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo LICENSE para detalles.

## Mejoras Futuras

- **Métodos Adicionales**: Algoritmos genéticos, optimización por enjambre de partículas
- **Visualización 3D**: Patrones de radiación tridimensionales
- **Herramientas de Optimización**: Optimización de diseño multi-objetivo
- **Integración de Mediciones**: Soporte para comparación de patrones medidos
- **Exportación Avanzada**: Formatos de archivo MATLAB, CST, HFSS