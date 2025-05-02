import colorsys
import random
from enum import Enum

import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium

from urban_transit_network_analysis.context.PrintGraphAnalysContext import PrintGraphAnalysContext
from urban_transit_network_analysis.context.MetricCalculationContext import MetricCalculationContext
"""
    Класс отрисовывающий графики по вычисленным метрикам 
"""


class Printer:
    def __init__(
            self,
            data,
            metric_calculation_context: MetricCalculationContext,
            city_name
    ):
        self.data = data
        self.metric_calculation_context = metric_calculation_context
        self.city_name = city_name

    def print_graphics(self, print_graph_analis_context: PrintGraphAnalysContext):
        for hist_metric in print_graph_analis_context.histogram_map_metrics_list:
            self.plot_histogram(hist_metric)
        for heat_map_metric in print_graph_analis_context.heat_map_metrics_list:
            self.plot_heatmap_on_map(heat_map_metric, print_graph_analis_context.mesh_size)
        for map_metric in print_graph_analis_context.map_clustering_list:
            self.plot_on_map_diff(map_metric)


    def plot_histogram(
            self,
            metric: Enum,
            title="Distribution of metric_value ",
            ylabel="Frequency"
    ):
        metric_name = str(metric.value)
        title += metric_name
        metric_values = self.data[metric_name + "_value"]

        df = pd.DataFrame({"metric_value: " + metric_name: metric_values})

        fig = px.histogram(
            df,
            x="metric_value: " + metric_name,
            title=title,
            labels={
                "metric_value ": metric_name,
                "count": ylabel
            },
            marginal="rug"
        )

        fig.show()

    def plot_heatmap_on_map(
            self,
            metric: Enum,
            resolution,
            colorscale='Viridis'
    ):
        latitudes = []
        longitudes = []
        metric_values = []
        metric_name = str(metric.value)

        for index in range(len(self.data[metric_name + "_identity"])):
            try:
                parsed_point = self.data[metric_name + "_identity"][index]
                lat, lon = parsed_point.latitude, parsed_point.longitude
                latitudes.append(float(lat))
                longitudes.append(float(lon))
                metric_values.append(self.data[metric_name + "_value"][index])
            except ValueError:
                print(f"Skipping invalid identity")

        df = pd.DataFrame({
            "latitude": latitudes,
            "longitude": longitudes,
            "metric_value": metric_values
        })
        df['metric_value'] = df['metric_value'].fillna(0)

        lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
        lon_min, lon_max = df['longitude'].min(), df['longitude'].max()

        lon_edges = np.linspace(lon_min, lon_max, resolution + 1)
        lat_edges = np.linspace(lat_min, lat_max, resolution + 1)

        lon_centers = (lon_edges[:-1] + lon_edges[1:]) / 2
        lat_centers = (lat_edges[:-1] + lat_edges[1:]) / 2

        avg_values = np.empty((resolution, resolution))
        avg_values.fill(0)

        for i in range(resolution):
            for j in range(resolution):
                mask = (
                        (df['longitude'] >= lon_edges[i]) &
                        (df['longitude'] < lon_edges[i + 1]) &
                        (df['latitude'] >= lat_edges[j]) &
                        (df['latitude'] < lat_edges[j + 1])
                )

                cell_points = df[mask]

                if len(cell_points) > 0:
                    mean_value = cell_points["metric_value"].mean()
                    avg_values[j, i] = 0 if np.isnan(mean_value) or np.isinf(mean_value) else mean_value

        fig = go.Figure()

        fig.add_trace(go.Heatmap(
            z=avg_values,
            x=lon_centers,
            y=lat_centers,
            colorscale=colorscale,
            colorbar=dict(title='Среднее значение метрики ' + metric_name),
            hoverinfo='x+y+z',
            name='Средние значения ' + metric_name,
        ))

        fig.show()

    def plot_on_map(
            self,
            metric: Enum
    ):

        latitudes = []
        longitudes = []
        metric_values = []
        metric_name = str(metric.value)

        for item in range(len(self.data[metric_name + "_identity"])):
            try:
                parsed_point = self.data[metric_name + "_identity"][item]
                lat, lon = parsed_point.longitude, parsed_point.latitude
                latitudes.append(float(lat))
                longitudes.append(float(lon))
                metric_values.append(self.data[metric_name + "_value"][item])
            except ValueError:
                print(f"Skipping invalid identity")

        df = pd.DataFrame({
            "latitude": latitudes,
            "longitude": longitudes,
            "metric_value": metric_values
        })

        lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
        lon_min, lon_max = df['longitude'].min(), df['longitude'].max()

        # Вычисляем центральные координаты (для центрирования карты)
        latitude = (lat_min + lat_max) / 2
        longitude = (lon_min + lon_max) / 2

        # Создаем карту, центрированную на DataFrame
        m = folium.Map(location=[longitude, latitude], zoom_start=12)

        min_metric = df['metric_value'].min()
        max_metric = df['metric_value'].max()

        # Добавьте точки на карту
        for i in range(len(df['metric_value'])):
            metric_value = df['metric_value'][i]
            radius = self.get_radius(metric_value, min_metric, max_metric)
            color = self.get_color(metric_value, min_metric, max_metric)

            folium.CircleMarker(
                location=[df['longitude'][i], df['latitude'][i]],
                radius=1,
                #color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=f"Metric Value: {metric_value:.2f}",
            ).add_to(m)

        m.save(self.city_name + "_map.html")

    def plot_on_map_diff(
            self,
            metric: Enum
    ):

        latitudes = []
        longitudes = []
        metric_values = []
        metric_name = str(metric.value)

        for item in range(len(self.data[metric_name + "_identity"])):
            try:
                parsed_point = self.data[metric_name + "_identity"][item]
                lat, lon = parsed_point.longitude, parsed_point.latitude
                latitudes.append(float(lat))
                longitudes.append(float(lon))
                metric_values.append(self.data[metric_name + "_value"][item])
            except ValueError:
                print(f"Skipping invalid identity")

        df = pd.DataFrame({
            "latitude": latitudes,
            "longitude": longitudes,
            "metric_value": metric_values
        })

        grouped = df.groupby("metric_value")

        lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
        lon_min, lon_max = df['longitude'].min(), df['longitude'].max()

        latitude = (lat_min + lat_max) / 2
        longitude = (lon_min + lon_max) / 2

        m = folium.Map(location=[longitude, latitude], zoom_start=12)

        for metric, group in grouped:
            color = self.get_new_color()
            coordinates = list(zip(group["latitude"], group["longitude"]))
            for point in coordinates:
                folium.CircleMarker(
                    location=[point[1], point[0]],
                    radius=1,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    popup=f"Metric Value: {metric:.2f}",
                ).add_to(m)

        m.save(self.city_name + "_" + metric_name + "_map.html")

    def get_radius(self, metric_value, min_metric, max_metric):
        normalized_value = self.normalize_metric(metric_value, min_metric, max_metric)
        min_radius = 2
        max_radius = 10
        return min_radius + (max_radius - min_radius) * normalized_value

    def get_new_color(self):
        hue = random.random()

        saturation = 0.5
        brightness = 0.8

        red, green, blue = colorsys.hsv_to_rgb(hue, saturation, brightness)

        red = int(red * 255)
        green = int(green * 255)
        blue = int(blue * 255)

        return f'#{red:02x}{green:02x}{blue:02x}'

    def normalize_metric(self, value, min_metric, max_metric):
        normalized_value = (value - min_metric) / (max_metric - min_metric)
        return normalized_value