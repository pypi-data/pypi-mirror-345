from urban_transit_network_analysis.context.MetricCalculationContext import MetricCalculationContext
from urban_transit_network_analysis.context.GraphAnalysContext import GraphAnalysContext

"""
    Контекст для анализа сетей
"""


class AnalysContext:
    def __init__(
            self,
            ru_city_name: str = None,
            common_metric_calculation_context: MetricCalculationContext = MetricCalculationContext(),
            graph_analis_context: [GraphAnalysContext] = None
    ):
        if graph_analis_context is None:
            graph_analis_context = [GraphAnalysContext()]
        self.ru_city_name = ru_city_name
        self.common_metric_calculation_context = common_metric_calculation_context
        for item in graph_analis_context:
            if item.metric_calculation_context is None:
                item.metric_calculation_context = common_metric_calculation_context
        self.graph_analis_context = graph_analis_context
