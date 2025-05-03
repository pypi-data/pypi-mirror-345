from enum import Enum
import urban_transit_network_analysis.database.GraphDbManager as GraphDbManager
"""
    Список типов сетей с соответсвующими конструкторами для классов работающими с бд
"""


class GraphTypes(Enum):
    ROAD_GRAPH = GraphDbManager.RoadGraphDBManager
    ROAD_BUILDINGS_GRAPH = GraphDbManager.RoadBuildingsDbManager
    BUS_GRAPH = GraphDbManager.BusGraphDBManager
    TRAM_GRAPH = GraphDbManager.TramGraphDBManager
    TROLLEY_GRAPH = GraphDbManager.TrolleyGraphDBManager
    MINIBUS_GRAPH = GraphDbManager.MiniBusGraphDBManager
