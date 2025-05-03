import random

from urban_transit_network_analysis.context.DBGraphParameters import DBGraphParameters
from urban_transit_network_analysis.context.MetricCalculationContext import MetricCalculationContext
from urban_transit_network_analysis.context.PrintGraphAnalysContext import PrintGraphAnalysContext
from urban_transit_network_analysis.enums.GraphTypes import GraphTypes

"""
    Контекст для анализа сети конкретной сети
"""


class GraphAnalysContext:
    def __init__(
            self,
            metric_calculation_context: MetricCalculationContext = MetricCalculationContext(),
            print_graph_analis_context: PrintGraphAnalysContext = PrintGraphAnalysContext(),
            graph_name: str = "SomeGraph" + str(random.random()),
            graph_type: GraphTypes = GraphTypes.ROAD_GRAPH,
            need_prepare_data: bool = True,
            need_calculate_and_print_data: bool = True,
            need_create_graph: bool = True,
            city_name: str = ""
    ):
        self.metric_calculation_context = metric_calculation_context
        self.graph_name = graph_name
        self.graph_type = graph_type
        self.need_prepare_data = need_prepare_data
        self.print_graph_analis_context = print_graph_analis_context
        self.need_calculate_and_print_data = need_calculate_and_print_data
        self.need_create_graph = need_create_graph
        self.neo4j_DB_graph_parameters = DBGraphParameters()
        self.city_name = city_name
