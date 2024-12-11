# Importación de librerías
import osmnx as ox
import folium
import rasterio
import numpy as np
from shapely.geometry import Polygon, LineString, Point
from geopandas import GeoDataFrame
import geopandas as gpd
import re
from pyproj import Transformer
from folium.plugins import HeatMap

# Configuración Global
ox.settings.use_cache = True
ox.settings.log_console = True
ox.settings.timeout = 60

# ------------------------- Funciones Auxiliares -------------------------

def parse_coordinates(input_string):
    """Extrae coordenadas de una cadena de texto."""
    matches = re.findall(r"[-+]?\d*\.\d+|\d+", input_string)
    if len(matches) >= 2:
        return float(matches[0]), float(matches[1])
    else:
        raise ValueError("No se encontraron coordenadas válidas en la entrada.")

def transform_coordinates(lat, lon, crs_src, crs_dst):
    """Transforma coordenadas entre sistemas de referencia."""
    transformer = Transformer.from_crs(crs_src, crs_dst, always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y

def process_dem(dem_path):
    """Procesa el archivo DEM y devuelve sus datos y límites."""
    with rasterio.open(dem_path) as dem:
        elevation = dem.read(1)
        transform = dem.transform
        cell_size = dem.res[0]
        crs_dem = str(dem.crs)

        dem_bounds = dem.bounds
        polygon = Polygon([
            (dem_bounds.left, dem_bounds.bottom),
            (dem_bounds.left, dem_bounds.top),
            (dem_bounds.right, dem_bounds.top),
            (dem_bounds.right, dem_bounds.bottom),
            (dem_bounds.left, dem_bounds.bottom)
        ])
        polygon_gdf = GeoDataFrame({'geometry': [polygon]}, crs=crs_dem)
        polygon_gdf = polygon_gdf.to_crs("EPSG:4326")
        polygon = polygon_gdf.geometry.iloc[0]

        return elevation, transform, cell_size, polygon, crs_dem

def generate_graph(polygon):
    """Genera un grafo de carreteras desde el polígono proporcionado."""
    try:
        graph = ox.graph_from_polygon(polygon, network_type="drive")
        return ox.graph_to_gdfs(graph, nodes=True, edges=True), graph
    except Exception as e:
        print(f"Error al generar el grafo: {e}")
        exit()

def calculate_visibility(dem, base_coords, radius, transform):
    """Calcula la visibilidad desde una estación base en el DEM."""
    visibility = np.zeros_like(dem, dtype=bool)
    base_row, base_col = base_coords
    base_height = dem[base_row, base_col]

    rows, cols = dem.shape
    for r in range(max(0, base_row - radius), min(rows, base_row + radius)):
        for c in range(max(0, base_col - radius), min(cols, base_col + radius)):
            if (r, c) == (base_row, base_col):
                visibility[r, c] = True
                continue
            line = LineString([(base_col, base_row), (c, r)])
            max_height = base_height
            for coord in line.coords[1:]:
                row, col = int(coord[1]), int(coord[0])
                if dem[row, col] > max_height:
                    break
                max_height = max(max_height, dem[row, col])
            else:
                visibility[r, c] = True
    return visibility

# ------------------------- Visualización del Mapa -------------------------

def create_map(edges, estaciones, radio_influencia, elevation, transform, cell_size, graph, inicio_coords, fin_coords, num_puntos_ruta):
    """Crea un mapa interactivo con visibilidad, rutas y áreas de influencia."""
    # Crear el mapa centrado en el primer punto del grafo
    centroid = edges.geometry.centroid.iloc[0]
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=14)

    # Añadir carreteras al mapa
    folium.GeoJson(edges, style_function=lambda x: {"color": "gray", "weight": 2}).add_to(m)

    # Añadir estaciones base con icono de antena y sus áreas de influencia
    for estacion in estaciones:
        folium.Marker(estacion, icon=folium.Icon(icon="signal", prefix="glyphicon", color="red"), popup="Estación Base").add_to(m)
        folium.Circle(location=estacion, radius=radio_influencia, color="blue", fill=True, fill_opacity=0.2).add_to(m)

    # Añadir puntos de inicio y fin
    folium.Marker(inicio_coords, icon=folium.Icon(color="green", icon="play"), popup="Inicio").add_to(m)
    folium.Marker(fin_coords, icon=folium.Icon(color="red", icon="stop"), popup="Fin").add_to(m)

    # Calcular ruta pasando por puntos intermedios
    try:
        inicio_nodo = ox.distance.nearest_nodes(graph, inicio_coords[1], inicio_coords[0])
        fin_nodo = ox.distance.nearest_nodes(graph, fin_coords[1], fin_coords[0])

        # Crear puntos intermedios entre inicio y fin
        linea_directa = LineString([Point(inicio_coords[1], inicio_coords[0]), Point(fin_coords[1], fin_coords[0])])
        puntos_intermedios = [linea_directa.interpolate(i, normalized=True) for i in np.linspace(0, 1, num_puntos_ruta + 2)[1:-1]]

        # Encontrar nodos más cercanos a los puntos intermedios
        nodos_intermedios = [ox.distance.nearest_nodes(graph, punto.x, punto.y) for punto in puntos_intermedios]

        # Crear una lista de todos los nodos de la ruta
        nodos_ruta = [inicio_nodo] + nodos_intermedios + [fin_nodo]

        # Calcular la ruta completa pasando por todos los nodos
        ruta_completa = []
        for i in range(len(nodos_ruta) - 1):
            tramo_ruta = ox.shortest_path(graph, nodos_ruta[i], nodos_ruta[i + 1], weight="length")
            if tramo_ruta:
                ruta_completa.extend(tramo_ruta[:-1])
        ruta_completa.append(nodos_ruta[-1])

        # Dibujar la ruta en el mapa
        ruta_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in ruta_completa]
        folium.PolyLine(ruta_coords, color="blue", weight=5).add_to(m)

        # Añadir paradas intermedias
        for punto in puntos_intermedios:
            folium.Marker([punto.y, punto.x], icon=folium.Icon(color="orange", icon="flag"), popup="Parada Intermedia").add_to(m)

    except Exception as e:
        print(f"Error al calcular la ruta: {e}")

    # Guardar mapa
    m.save("mapa_final.html")
    print("El mapa se ha guardado como 'mapa_final.html'.")

# ------------------------- Ejecución del Programa Principal -------------------------

def main():
    place_name = input("\nIntroduce el nombre del lugar: ")
    num_estaciones = int(input("Introduce el número de estaciones base: "))
    estaciones = [parse_coordinates(input(f"Introduce las coordenadas de la estación base {i + 1}: ")) for i in range(num_estaciones)]
    radio_influencia = float(input("Introduce el radio de influencia en metros: "))
    inicio_coords = parse_coordinates(input("Introduce las coordenadas del punto de inicio: "))
    fin_coords = parse_coordinates(input("Introduce las coordenadas del punto de fin: "))
    num_puntos_ruta = int(input("Introduce el número de puntos aleatorios en la ruta: "))
    dem_path = input("Introduce la ruta al archivo DEM: ")

    elevation, transform, cell_size, polygon, crs_dem = process_dem(dem_path)
    (nodes, edges), graph = generate_graph(polygon)

    create_map(edges, estaciones, radio_influencia, elevation, transform, cell_size, graph, inicio_coords, fin_coords, num_puntos_ruta)

if __name__ == "__main__":
    main()