import math
import Orange
from Orange.widgets.widget import OWWidget
from Orange.widgets.utils.concurrent import ConcurrentWidgetMixin  # widget --> tareas en paralelo
import requests

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from math import radians, cos, sqrt

import Orange.data.pandas_compat as pc
from Orange.widgets import gui, widget
from Orange.widgets.widget import Output, Msg
from PyQt5.QtWidgets import QLineEdit, QLabel, QComboBox, QDoubleSpinBox, QDateEdit, QPushButton, QVBoxLayout, \
    QHBoxLayout

import pandas as pd
import geopandas as gpd

from Orange.widgets.utils.widgetpreview import WidgetPreview


class oweqcatalogdownload(OWWidget, ConcurrentWidgetMixin):
    name = "EQ Catalog Download"
    description = "Remotely acquire earthquake data using Open Data APIs"
    icon = "icons/EQCatalogDownload.png"
    keywords = "earthquakes, acquire, api, data, catalog, download, sismology, etl"
    priority = 2240

    want_main_area = False

    resizing_enabled = False

    settings_version = 3

    class Error(widget.OWWidget.Error):
        generation_error = Msg("{}")

    class Outputs:
        data = Output("Catalog", Orange.data.Table)
        configuration_table = Output("Catalog Configuration Table", Orange.data.Table)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        ConcurrentWidgetMixin.__init__(self)
        self.controlArea.setMinimumWidth(360)

        self.data = None

        box_data_source = gui.widgetBox(self.controlArea, "Data Source")
        self.data_source_combobox = QComboBox(self)
        self.data_source_combobox.addItems(["USGS", "Chile Sismology"])
        gui.widgetLabel(box_data_source, "Choose the data source:")
        box_data_source.layout().addWidget(self.data_source_combobox)
        self.data_source_combobox.editTextChanged.connect(self.configurations_table)

        box_time = gui.widgetBox(self.controlArea, "Period of time")
        self.start_date = QDateEdit(self)
        self.end_date = QDateEdit(self)
        self.start_date.setCalendarPopup(True)
        self.end_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        gui.widgetLabel(box_time, "Start Date:")
        box_time.layout().addWidget(self.start_date)
        self.start_date.timeChanged.connect(self.configurations_table)
        gui.widgetLabel(box_time, "End Date:")
        new_date = datetime(2000, 11, 1)
        self.end_date.setDate(new_date)
        box_time.layout().addWidget(self.end_date)
        self.end_date.timeChanged.connect(self.configurations_table)

        box_magnitude = gui.widgetBox(self.controlArea, "Min Magnitude")
        self.min_magnitude = QDoubleSpinBox(self)
        self.min_magnitude.setRange(0.0, 10.0)
        self.min_magnitude.setSingleStep(0.1)
        self.min_magnitude.setValue(5.0)
        gui.widgetLabel(box_magnitude, "Filter by magnitude:")
        box_magnitude.layout().addWidget(self.min_magnitude)
        self.min_magnitude.textChanged.connect(self.configurations_table)

        box_place = gui.widgetBox(self.controlArea, "Place")
        self.place_combobox = QComboBox(self)
        self.place_combobox.addItems(
            ["By coordinates of a rectangle", "By coordinates of the center of a circle and its radius"])
        gui.widgetLabel(box_place, "How do you want to find the place?:")
        box_place.layout().addWidget(self.place_combobox)
        self.place_combobox.editTextChanged.connect(self.configurations_table)

        self.dynamic_layout = QVBoxLayout()
        box_place.layout().addLayout(self.dynamic_layout)

        self.place_combobox.currentIndexChanged.connect(self.update_place_fields)
        self.update_place_fields()

        toplayout = QHBoxLayout()
        toplayout.setContentsMargins(0, 0, 0, 0)
        box_data_source.layout().addLayout(toplayout)

        # Botón Generate
        button_box = gui.widgetBox(self.controlArea, addSpace=True, margin=10)
        self.btn_generate = QPushButton("Generate", toolTip="Cargar datos.")
        self.btn_generate.setMinimumWidth(10)
        self.btn_generate.clicked.connect(self.generate)
        self.btn_generate.setEnabled(False)
        button_box.layout().addWidget(self.btn_generate)

        self.btn_reset = QPushButton("Reset", toolTip="Reset node.")
        self.btn_reset.setMinimumWidth(10)
        self.btn_reset.clicked.connect(self.reset_node)
        button_box.layout().addWidget(self.btn_reset)

    def update_place_fields(self):
        for i in reversed(range(self.dynamic_layout.count())):
            widget_to_remove = self.dynamic_layout.itemAt(i).widget()
            self.dynamic_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

        if self.place_combobox.currentText() == "By coordinates of a rectangle":
            self.min_latitude = QLineEdit(self)
            self.max_latitude = QLineEdit(self)
            self.min_longitude = QLineEdit(self)
            self.max_longitude = QLineEdit(self)

            self.dynamic_layout.addWidget(QLabel("Min Latitude:"))
            self.dynamic_layout.addWidget(self.min_latitude)
            self.min_latitude.textChanged.connect(self.field_check_cuadrado)
            self.min_latitude.textChanged.connect(self.configurations_table)
            self.dynamic_layout.addWidget(QLabel("Max Latitude:"))
            self.dynamic_layout.addWidget(self.max_latitude)
            self.max_latitude.textChanged.connect(self.field_check_cuadrado)
            self.max_latitude.textChanged.connect(self.configurations_table)
            self.dynamic_layout.addWidget(QLabel("Min Longitude:"))
            self.dynamic_layout.addWidget(self.min_longitude)
            self.min_longitude.textChanged.connect(self.field_check_cuadrado)
            self.min_longitude.textChanged.connect(self.configurations_table)
            self.dynamic_layout.addWidget(QLabel("Max Longitude:"))
            self.dynamic_layout.addWidget(self.max_longitude)
            self.max_longitude.textChanged.connect(self.field_check_cuadrado)
            self.max_longitude.textChanged.connect(self.configurations_table)

        else:
            self.latitude = QLineEdit(self)
            self.longitude = QLineEdit(self)
            self.maxradiuskm = QLineEdit(self)

            self.dynamic_layout.addWidget(QLabel("Latitude:"))
            self.dynamic_layout.addWidget(self.latitude)
            self.latitude.textChanged.connect(self.field_check_circulo)
            self.latitude.textChanged.connect(self.configurations_table)
            self.dynamic_layout.addWidget(QLabel("Longitude:"))
            self.dynamic_layout.addWidget(self.longitude)
            self.longitude.textChanged.connect(self.field_check_circulo)
            self.longitude.textChanged.connect(self.configurations_table)
            self.dynamic_layout.addWidget(QLabel("Max radius (km):"))
            self.dynamic_layout.addWidget(self.maxradiuskm)
            self.maxradiuskm.textChanged.connect(self.field_check_circulo)
            self.maxradiuskm.textChanged.connect(self.configurations_table)

    def generate(self):
        if str(self.place_combobox.currentText()) == "By coordinates of a rectangle":
            min_lat = float(self.min_latitude.text().replace(',', '.'))
            max_lat = float(self.max_latitude.text().replace(',', '.'))
            min_lon = float(self.min_longitude.text().replace(',', '.'))
            max_lon = float(self.max_longitude.text().replace(',', '.'))

            if str(self.data_source_combobox.currentText()) == "Chile Sismology":
                if not self.validar_rectangulo_en_chile(min_lat, max_lat, min_lon, max_lon):
                    self.Error.generation_error.clear()
                    self.Error.generation_error("The coordinates do not belong to Chile")
                    return

            else:
                if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
                    self.Error.generation_error("Latitude must be between -90 and 90.")
                    return
                if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
                    self.Error.generation_error("Longitude must be between -180 and 180.")
                    return
                self.Error.generation_error.clear()

            if self.end_date.date() < self.start_date.date():
                self.Error.generation_error("The end date must be after the start date.")
                return
            self.Error.generation_error.clear()

            response = self.get_earthquake_rectangle_data()

        else:
            if str(self.data_source_combobox.currentText()) == "Chile Sismology":
                if not self.validar_circulo_en_chile(self.latitude, self.longitude, self.maxradiuskm):
                    self.Error.generation_error("The coordinates do not belong to Chile.")
                    self.btn_generate.setEnabled(False)
                    return
            else:
                radius = float(self.maxradiuskm.text().replace(',', '.'))
                if radius <= 0:
                    self.Error.generation_error("Radius must be a positive number.")
                    return
                self.Error.generation_error.clear()

            if self.end_date.date() < self.start_date.date():
                self.Error.generation_error("The end date must be after the start date.")
                return
            self.Error.generation_error.clear()

            response = self.get_earthquake_circle_data()

        if str(self.data_source_combobox.currentText()) == "USGS":
            exportDf = self.obtener_datos_usgs(response)
            if exportDf.empty:
                self.Error.generation_error("No event matching these characteristics was found.")
            else:
                exportDf['place'] = exportDf['place'].astype('category')
                exportDf.sort_values('time', ascending=True, inplace=True)
                out_data = pc.table_from_frame(exportDf)
        else:
            exportDf = self.obtener_datos_sismos_rango(self.start_date, self.end_date)
            if exportDf.empty:
                self.Error.generation_error("No event matching these characteristics was found.")
            else:
                exportDf['place'] = exportDf['place'].astype('category')
                exportDf.sort_values('time', ascending=True, inplace=True)
                out_data = pc.table_from_frame(exportDf)

        self.configurations_table()

        self.Outputs.data.send(out_data)

    def get_earthquake_rectangle_data(self):
        fecha_inicio = str(self.start_date.text().replace("/", "-"))
        fecha_fin = str(self.end_date.text().replace("/", "-"))
        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={fecha_inicio}&endtime={fecha_fin}" \
              f"&minmagnitude={str(self.min_magnitude.text())}&minlatitude={str(self.min_latitude.text())}" \
              f"&maxlatitude={str(self.max_latitude.text())}&minlongitude={str(self.min_longitude.text())}" \
              f"&maxlongitude={str(self.max_longitude.text())}"
        url_formato = url.replace(",", ".")
        response = requests.get(url_formato)

        if response.status_code == 200:
            response = response.json()
            return response
        else:
            return f"Error en la solicitud: {response.status_code}"

    def get_earthquake_circle_data(self):
        fecha_inicio = str(self.start_date.text().replace("/", "-"))
        fecha_fin = str(self.end_date.text().replace("/", "-"))
        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={fecha_inicio}&endtime={fecha_fin}" \
              f"&minmagnitude={str(self.min_magnitude.text())}&latitude={str(self.latitude.text())}&longitude={str(self.longitude.text())}" \
              f"&maxradiuskm={str(self.maxradiuskm.text())}"
        print(url)
        url_formato = url.replace(",", ".")
        response = requests.get(url_formato)

        if response.status_code == 200:
            response = response.json()
            return response
        else:
            return f"Error en la solicitud: {response.status_code}"

    # USGS
    def obtener_datos_usgs(self, response):
        self.progressBarInit()
        exportDf = gpd.GeoDataFrame()
        for i, data in enumerate(response['features']):
            coord = data['geometry']['coordinates']
            geometry = gpd.points_from_xy([coord[0]], [coord[1]])
            gdf = gpd.GeoDataFrame(data['properties'], index=[i], geometry=geometry, crs='EPSG:4326')
            gdf = gdf[['mag', 'place', 'time', 'alert', 'status', 'tsunami', 'geometry']]

            gdf['time'] = datetime(1970, 1, 1) + timedelta(seconds=gdf['time'][i]/1000)

            gdf['time'] = gdf['time'].dt.strftime('%Y-%m-%d %H:%M:%S')

            gdf['latitude'] = gdf['geometry'].apply(lambda point: point.x)
            gdf['longitude'] = gdf['geometry'].apply(lambda point: point.y)

            df = pd.DataFrame(gdf.drop('geometry', axis=1))

            df = df[['mag', 'place', 'latitude', 'longitude', 'time', 'alert', 'status', 'tsunami']]

            exportDf = pd.concat([exportDf, df])

            self.progressBarSet((i + 1) * 100 / len(response['features']))

        self.progressBarFinished()
        return exportDf

    def generar_url(self, fecha):
        return f"https://www.sismologia.cl/sismicidad/catalogo/{fecha.year()}/{fecha.month():02}/{fecha.year()}" \
               f"{fecha.month():02}{fecha.day():02}.html"


    def obtener_datos_sismos(self, fecha):
        url = self.generar_url(fecha)
        response = requests.get(url)
        if response.status_code != 200:
            print(f"No se pudo acceder a los datos para la fecha {fecha}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        tabla = soup.find('table', class_='sismologia detalle')
        if not tabla:
            print(f"No se encontró tabla de sismos para la fecha {fecha}")
            return []

        datos_sismos = []
        for fila in tabla.find_all('tr')[1:]:  # Omitir la primera fila de encabezado
            columnas = fila.find_all('td')
            if len(columnas) < 5:
                continue

            latitud_longitud = columnas[2].text.strip().split(" ")
            distance_part = columnas[0].text[19:]
            time = columnas[1].text

            # Latitud y longitud juntas (se salta la fila)
            if len(latitud_longitud) == 1:
                continue

            # Latitud o longitud vacias (se salta la fila)
            if latitud_longitud[0] == '' or latitud_longitud[1] == '':
                continue

            latitud = float(latitud_longitud[0])
            longitud = float(latitud_longitud[1])
            magnitud = float(columnas[4].text.strip().split()[0])  # Obtener solo el número

            if str(self.place_combobox.currentText()) == "By coordinates of a rectangle":
                bool = self.punto_en_rectangulo(latitud, longitud, self.min_latitude, self.max_latitude,
                                                self.min_longitude, self.max_longitude)
            else:
                bool = self.punto_en_circulo(latitud, longitud, self.latitude, self.longitude, self.maxradiuskm)

            if magnitud >= self.min_magnitude.value():
                if bool:
                    datos_sismos.append({
                        "mag": magnitud,
                        "place": f"{distance_part}",
                        "latitude": latitud,
                        "longitude": longitud,
                        "time": time,
                        "alert": None,
                        "status": None,
                        "tsunami": None
                    })

        return datos_sismos

    def obtener_datos_sismos_rango(self, fecha_inicio, fecha_fin):
        self.progressBarInit()
        fecha_actual = fecha_inicio.date()
        fecha_fin = fecha_fin.date()
        todos_sismos = []

        dias_totales = (fecha_fin.toPyDate() - fecha_actual.toPyDate()).days + 1

        i = 0
        while fecha_actual <= fecha_fin:
            sismos = self.obtener_datos_sismos(fecha_actual)
            todos_sismos.extend(sismos)
            fecha_actual = fecha_actual.addDays(1)
            i += 1
            # Barra de progreso
            self.progressBarSet((i + 1) * 100 / dias_totales)

        exportDf = pd.DataFrame(todos_sismos)

        self.progressBarFinished()

        return exportDf

    def configurations_table(self):
        df = pd.DataFrame()
        df['Magnitude'] = [self.min_magnitude.text().replace(',', '.')]
        df['Start Date'] = [str(self.start_date.text())]
        df['End Date'] = [str(self.end_date.text())]
        df['Data Source'] = [str(self.data_source_combobox.currentText())]

        if self.place_combobox.currentText() == "By coordinates of a rectangle":
            df['Place'] = ["Rectangle"]
            df['Min Latitude'] = [self.min_latitude.text().replace(',', '.')]
            df['Max Latitude'] = [str(self.max_latitude.text().replace(',', '.'))]
            df['Min Longitude'] = [str(self.min_longitude.text().replace(',', '.'))]
            df['Max Longitude'] = [str(self.max_longitude.text().replace(',', '.'))]
            df['Max Radius Km'] = None
        else:
            df['Place'] = ["Circle"]
            df['Min Latitude'] = [str(self.latitude.text().replace(',', '.'))]
            df['Min Longitude'] = [str(self.longitude.text().replace(',', '.'))]
            df['Max Longitude'] = None
            df['Max Latitude'] = None
            df['Max Radius Km'] = [str(self.maxradiuskm.text().replace(',', '.'))]

        out_configurations = pc.table_from_frame(df)
        self.Outputs.configuration_table.send(out_configurations)

    def punto_en_rectangulo(self, lat_punto, lon_punto, lat_min, lat_max, lon_min, lon_max):
        lat_min = float(lat_min.text().replace(",", "."))  # Reemplazar coma por punto y convertir a float
        lat_max = float(lat_max.text().replace(",", "."))
        lon_min = float(lon_min.text().replace(",", "."))
        lon_max = float(lon_max.text().replace(",", "."))
        lat_punto = float(lat_punto)
        lon_punto = float(lon_punto)

        # Primero, verificamos si la latitud está dentro del rango.
        if not (lat_min <= lat_punto <= lat_max):
            return False

        # Ajustamos la longitud del punto para que esté en el rango [-180, 180]
        lon_punto = (lon_punto + 180) % 360 - 180
        lon_min = (lon_min + 180) % 360 - 180
        lon_max = (lon_max + 180) % 360 - 180

        # Si el rectángulo cruza la línea internacional de cambio de fecha
        if lon_min > lon_max:
            # El punto está dentro si su longitud está fuera de este rango específico
            return lon_punto >= lon_min or lon_punto <= lon_max
        else:
            # Para rectángulos que no cruzan la línea de cambio de fecha
            return lon_min <= lon_punto <= lon_max

    def punto_en_circulo(self, lat_punto, lon_punto, lat_centro, lon_centro, radio):
        R = 6371.0

        latitud = lat_punto
        longitud = lon_punto

        lat_centro = float(lat_centro.text().replace(',', '.'))
        lon_centro = float(lon_centro.text().replace(',', '.'))

        lat_centro = radians(lat_centro)
        lon_centro = radians(lon_centro)
        lat_punto = radians(latitud)
        lon_punto = radians(longitud)

        dlat = lat_punto - lat_centro
        dlon = lon_punto - lon_centro

        a = pow(math.sin(dlat / 2), 2) + cos(lat_centro) * cos(lat_punto) * pow(math.sin(dlon / 2), 2)
        c = 2 * math.atan2(sqrt(a), sqrt(1 - a))
        distancia = R * c

        return distancia <= float(radio.text().replace(',', '.'))

    def field_check_cuadrado(self):
        all_filled = all(
            field.text() for field in [self.min_latitude, self.min_longitude, self.max_longitude, self.max_latitude])
        self.btn_generate.setEnabled(all_filled)

    def field_check_circulo(self):
        all_filled = all(field.text() for field in [self.latitude, self.longitude, self.maxradiuskm])
        self.btn_generate.setEnabled(all_filled)

    def validar_rectangulo_en_chile(self, latitud_min, latitud_max, longitud_min, longitud_max):
        latitud_max_chile = -18  # Latitud máxima de Chile (norte)
        latitud_min_chile = -56  # Latitud mínima de Chile (sur)
        longitud_max_chile = -64  # Longitud máxima de Chile (este)
        longitud_min_chile = -82  # Longitud mínima de Chile (oeste)

        # Verificar si el rectángulo está completamente dentro de los límites de Chile
        if latitud_min < latitud_min_chile or latitud_max > latitud_max_chile:
            return False
        if longitud_min < longitud_min_chile or longitud_max > longitud_max_chile:
            return False

        return True

    def validar_circulo_en_chile(self, latitud, longitud, radio_max_km):
        latitud_max_chile = -18  # Norte
        latitud_min_chile = -56  # Sur
        longitud_max_chile = -64  # Este
        longitud_min_chile = -82  # Oeste

        # Radio de la Tierra en km (para usar en Haversine)
        radio_tierra_km = 6371.0

        def distancia_haversine(lat1, lon1, lat2, lon2):
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return radio_tierra_km * c

        lat_c = float(latitud.text().replace(',', '.'))
        lon_c = float(longitud.text().replace(',', '.'))
        rad = float(radio_max_km.text().replace(',', '.'))

        # Verificar que el centro esté dentro de Chile
        if lat_c < latitud_min_chile or lat_c > latitud_max_chile:
            return False
        if lon_c < longitud_min_chile or lon_c > longitud_max_chile:
            return False

        # Definir los puntos extremos (límites de Chile en cada dirección)
        puntos_extremos = [
            (latitud_max_chile, lon_c),  # Norte
            (latitud_min_chile, lon_c),  # Sur
            (lat_c, longitud_max_chile),  # Este
            (lat_c, longitud_min_chile)  # Oeste
        ]

        # Verificar que el radio no exceda la distancia al límite en ninguna dirección
        for punto in puntos_extremos:
            dist = distancia_haversine(lat_c, lon_c, punto[0], punto[1])
            if rad > dist:
                return False

        return True

    def reset_node(self):
        self.clear()

        self.Outputs.data.send(None)

        self.min_magnitude.setValue(5.0)
        self.data_source_combobox.setCurrentText('USGS')
        new_date = datetime(2000, 1, 1)
        self.start_date.setDate(new_date)
        self.end_date.setDate(new_date)

        if self.place_combobox.currentText() == "By coordinates of a rectangle":
            self.min_latitude.setText("")
            self.max_latitude.setText("")
            self.min_longitude.setText("")
            self.max_longitude.setText("")
        else:
            self.latitude.setText("")
            self.longitude.setText("")
            self.maxradiuskm.setText("")

        self.place_combobox.setCurrentText("By coordinates of a rectangle")

        self.Outputs.configuration_table.send(None)

    def clear(self):
        self.Error.generation_error.clear()

if __name__ == "__main__":
    WidgetPreview(oweqcatalogdownload).run()