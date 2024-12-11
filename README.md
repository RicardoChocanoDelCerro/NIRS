# Documentación del Script de Generación de Mapas con Visibilidad y Rutas

Este proyecto consiste en un script en Python que realiza las siguientes tareas principales:

1. **Procesamiento de un Modelo Digital de Elevación (DEM)** para obtener información del relieve, su resolución y límites geográficos.

2. **Generación de un grafo de carreteras** a partir de un polígono definido por el área abarcada por el DEM, utilizando **OSMnx** para obtener datos de vías desde OpenStreetMap.

3. **Cálculo de áreas visibles** desde una o varias estaciones base en función del relieve (visibilidad lineal).

4. **Creación de un mapa interactivo** empleando **Folium**, en el cual se representan:
    - Las estaciones base.
    - La visibilidad en forma de mapa de calor.
    - El grafo de carreteras.
    
El resultado es un archivo HTML que despliega un mapa interactivo con toda la información integrada.

## Requisitos Previos

- **Python 3.7+**  
  El script ha sido probado en versiones recientes de Python (3.7 o superior).

- **Librerías de Python**:
  - [OSMnx](https://osmnx.readthedocs.io/)
  - [Folium](https://python-visualization.github.io/folium/)
  - [Folium Plugins](https://python-visualization.github.io/folium/plugins.html) (para HeatMap)
  - [Rasterio](https://rasterio.readthedocs.io/)
  - [NumPy](https://numpy.org/)
  - [Shapely](https://shapely.readthedocs.io/)
  - [GeoPandas](https://geopandas.org/)
  - [re (módulo estándar de Python)](https://docs.python.org/3/library/re.html)
  - [pyproj](https://pyproj4.github.io/pyproj/stable/)

**Nota:** Se asume que el entorno ya tiene instalados `pip` y `venv` para la gestión y creación de entornos virtuales. Si no es así, revisar la documentación oficial de Python.

## Instalación y Configuración del Entorno

1. **Clonar o descargar el repositorio** donde se encuentra el script principal (`.py`).

2. **Crear y activar un entorno virtual (opcional, pero recomendado)**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # En Windows: venv\Scripts\activate

## Instalación de Dependencias

Para instalar las dependencias necesarias, ejecute:

```bash
pip install osmnx folium rasterio numpy shapely geopandas pyproj

En algunos entornos, la instalación de geopandas y osmnx puede requerir librerías del sistema. Por ejemplo, en Ubuntu/Debian:

sudo apt-get update
sudo apt-get install libspatialindex-dev libgdal-dev

pip install geopandas osmnx

Uso del Script

Ejecutar desde la línea de comandos:

python main.py

El script solicitará la siguiente información por consola:

Nombre del lugar: Se utiliza internamente, no es obligatorio para un cálculo.
Número de estaciones base: Cantidad de puntos (estaciones) desde donde se calcula la visibilidad.
Coordenadas de cada estación base: Formato <latitud> <longitud>. Ejemplo: 40.4168 -3.7038.
Radio de influencia en metros: Alcance radial en metros para calcular visibilidad alrededor de cada estación.
Coordenadas del punto de inicio y fin: Pueden emplearse para referencia o rutas.
Número de puntos aleatorios en la ruta: Parámetro reservado para posibles funciones futuras.
Ruta al archivo DEM: Path completo o relativo al archivo raster del DEM (ej: ./dem_data.tif).
Una vez ingresados estos datos, el script:

Procesa el DEM: Extrae elevaciones, resolución, CRS y el polígono de cobertura.
Genera el grafo de vías a partir de OSMnx dentro del área del DEM.
Calcula la visibilidad desde las estaciones base.
Crea un mapa interactivo con Folium, que incluye:
Grafo de carreteras.
Marcadores de estaciones base.
Mapa de calor de visibilidad.
El resultado se guarda como mapa_final.html, que puede abrirse en cualquier navegador.

Estructura Interna del Código

Funciones Auxiliares:
parse_coordinates(input_string): Extrae coordenadas (lat, lon) de una cadena.
transform_coordinates(lat, lon, crs_src, crs_dst): Convierte coordenadas entre distintos sistemas de referencia.
check_coords_in_range(coords, dem_shape, transform): Verifica si unas coordenadas están dentro del rango del DEM.
calculate_visibility(dem, base_coords, radius, transform): Determina la visibilidad desde una estación base sobre el DEM.
Procesamiento del DEM (process_dem(dem_path)): Abre el DEM con Rasterio, obtiene la matriz de elevación, el transform, el crs, el tamaño de celda y el polígono que representa la extensión del DEM en EPSG:4326.
Generación del Grafo (generate_graph(polygon)): Utiliza OSMnx para descargar y generar un grafo de carreteras en el polígono especificado.
Creación del Mapa (create_map(...)): Crea un mapa Folium, añade capas con edges (carreteras), marcadores de estaciones y un HeatMap con la visibilidad calculada.
Función Principal main(): Recopila la información del usuario, procesa el DEM, genera el grafo y crea el mapa final.
Notas Adicionales

La precisión de la visibilidad depende de la resolución espacial del DEM.
El cálculo de visibilidad es simplificado (visión lineal); cualquier célula más alta en el camino bloquea la línea de vista.
La generación del grafo requiere conexión a Internet para consultar datos de OpenStreetMap.
Ajustar el CRS del DEM en el código si se utiliza otro modelo distinto a EPSG:32630.
Licencia

Este código se proporciona bajo la licencia MIT. Consulte el archivo LICENSE (si existe en el repositorio) para más detalles.

# MakeFile

sudo apt-get install make
- Crear entorno virtual
    make create-env

    Esto creará un entorno virtual en la carpeta venv.

- Instalar dependencias
    make install-deps

    Esto instalará las dependencias listadas en requirements.txt dentro del entorno virtual.

- Ejecución normal
    make run

    Esto creará el entorno virtual (si no existe), instalará las dependencias (si no están instaladas) y ejecutará main.py.

- Recarga automática (watch):
    make watch

    Esto ejecutará main.py y lo recargará automáticamente cada vez que se modifique un archivo .py en el directorio. Requiere tener instalado entr.
