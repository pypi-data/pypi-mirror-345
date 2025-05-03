from urban_transit_network_analysis.context import GraphAnalysContext
from urban_transit_network_analysis.database.CommunityDetection import Leiden, Louvain
from urban_transit_network_analysis.database.MetricsCalculate import Betweenness, PageRank
"""
    Класс записывающий метрики сетей в бд
"""


class MetricDataPreparer:
    def __init__(self, graph_analisis_context: GraphAnalysContext):
        self.leiden_calculator = None
        self.louvain_calculator = None
        self.betweenessens_calculator = None
        self.page_rank_calculator = None
        metric_calculation_context = graph_analisis_context.metric_calculation_context
        if metric_calculation_context.need_leiden_community_id or metric_calculation_context.need_leiden_modulariry:
            self.leiden_calculator = Leiden()
        if metric_calculation_context.need_louvain_community_id or metric_calculation_context.need_louvain_modulariry:
            self.louvain_calculator = Louvain()
        if metric_calculation_context.need_betweenessens:
            self.betweenessens_calculator = Betweenness()
        if metric_calculation_context.need_page_rank:
            self.page_rank_calculator = PageRank()
        self.graph_analisis_context = graph_analisis_context

    def prepare_metrics(self):
        result = {}
        if self.leiden_calculator is not None:
            result["leiden_modularity_value"] = self.prepare_leiden()
        if self.louvain_calculator is not None:
            result["louvain_modularity_value"] = self.prepare_louvain()
        if self.betweenessens_calculator is not None:
            self.prepare_betweenessens()
        if self.page_rank_calculator is not None:
            self.prepare_page_rank()
        return result

    def prepare_leiden(self):
        result = self.leiden_calculator.detect_communities(
            self.graph_analisis_context.graph_name,
            self.graph_analisis_context.neo4j_DB_graph_parameters.weight
        )
        print(result)
        print(f"LeidenAlgorithm Community detection for graph {self.graph_analisis_context.graph_name} completed.")
        return result

    def prepare_louvain(self):
        result = self.louvain_calculator.detect_communities(
            self.graph_analisis_context.graph_name,
            self.graph_analisis_context.neo4j_DB_graph_parameters.weight
        )
        print(result)
        print(f"LovainAlgorithm Community detection for graph {self.graph_analisis_context.graph_name} completed.")
        return result

    def prepare_betweenessens(self):
        self.betweenessens_calculator.metric_calculate(
            self.graph_analisis_context.graph_name,
            self.graph_analisis_context.neo4j_DB_graph_parameters.weight
        )
        print(f"betweenessens metric calculated for graph {self.graph_analisis_context.graph_name}.")

    def prepare_page_rank(self):
        self.page_rank_calculator.metric_calculate(
            self.graph_analisis_context.graph_name,
            self.graph_analisis_context.neo4j_DB_graph_parameters.weight
        )
        print(f"pageRank metric calculated for graph {self.graph_analisis_context.graph_name}.")

