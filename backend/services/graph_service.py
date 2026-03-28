"""
services/graph_service.py - Dependency Graph Service
=====================================================
Builds and manages dependency graphs using NetworkX.
Provides centrality analysis to identify critical files and modules.
"""

from typing import Dict, List, Any, Optional

import networkx as nx

from core.constants import NodeType, EdgeType, MAX_GRAPH_DEPTH
from core.logger import get_logger

logger = get_logger(__name__)


class GraphService:
    """
    Builds and analyzes dependency graphs for repositories.

    Uses NetworkX DiGraph to represent:
        - Nodes: files, modules, classes, functions
        - Edges: imports, calls, inheritance, dependencies

    Provides:
        - Centrality metrics (betweenness, degree, PageRank)
        - Critical file identification
        - Subgraph extraction
        - Graph serialization for API responses
    """

    def __init__(self):
        self.graph: nx.DiGraph = nx.DiGraph()

    def build_from_parsed_data(
        self,
        files: List[Dict[str, Any]],
        parsed_structures: Dict[str, Dict[str, Any]],
    ) -> nx.DiGraph:
        """
        Build a dependency graph from parsed file data.

        Args:
            files: List of file metadata dicts from ParserService.
            parsed_structures: Map of file_path → parsed structure (imports, classes, etc.).

        Returns:
            The constructed NetworkX DiGraph.
        """
        self.graph.clear()

        # Add file nodes
        for file_info in files:
            rel_path = file_info["relative_path"]
            self.graph.add_node(
                rel_path,
                type=NodeType.FILE,
                language=file_info["language"],
                line_count=file_info.get("line_count", 0),
            )

        # Add edges from import relationships
        for file_path, structure in parsed_structures.items():
            for imp in structure.get("imports", []):
                target_module = imp.get("module", "")
                if target_module:
                    # Resolve module to a file path (simplified)
                    target_path = self._resolve_module_to_file(target_module, files)
                    if target_path:
                        self.graph.add_edge(
                            file_path,
                            target_path,
                            type=EdgeType.IMPORTS,
                        )

        logger.info(
            "Dependency graph built",
            nodes=self.graph.number_of_nodes(),
            edges=self.graph.number_of_edges(),
        )
        return self.graph

    def get_critical_files(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Identify the most critical files based on graph centrality metrics.

        Uses betweenness centrality (how many shortest paths pass through a node)
        and in-degree (how many files depend on this file).

        Returns:
            Sorted list of dicts with file_path, betweenness, in_degree, pagerank.
        """
        if self.graph.number_of_nodes() == 0:
            return []

        betweenness = nx.betweenness_centrality(self.graph)
        in_degrees = dict(self.graph.in_degree())

        try:
            pagerank = nx.pagerank(self.graph, alpha=0.85)
        except nx.PowerIterationFailedConvergence:
            pagerank = {node: 0.0 for node in self.graph.nodes()}

        # Combine metrics into a composite score
        critical = []
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            if node_data.get("type") != NodeType.FILE:
                continue

            score = (
                betweenness.get(node, 0) * 0.4
                + (in_degrees.get(node, 0) / max(self.graph.number_of_nodes(), 1)) * 0.3
                + pagerank.get(node, 0) * 0.3
            )

            critical.append({
                "file_path": node,
                "composite_score": round(score, 6),
                "betweenness_centrality": round(betweenness.get(node, 0), 6),
                "in_degree": in_degrees.get(node, 0),
                "pagerank": round(pagerank.get(node, 0), 6),
            })

        critical.sort(key=lambda x: x["composite_score"], reverse=True)
        return critical[:top_n]

    def get_subgraph(self, node_id: str, depth: int = 2) -> Dict[str, Any]:
        """
        Extract a subgraph centered on a specific node up to a given depth.

        Useful for visualizing local dependencies of a file.
        """
        depth = min(depth, MAX_GRAPH_DEPTH)

        if node_id not in self.graph:
            return {"nodes": [], "edges": []}

        # BFS to find reachable nodes within depth
        reachable = set()
        reachable.add(node_id)
        frontier = {node_id}

        for _ in range(depth):
            next_frontier = set()
            for n in frontier:
                next_frontier.update(self.graph.successors(n))
                next_frontier.update(self.graph.predecessors(n))
            reachable.update(next_frontier)
            frontier = next_frontier

        subgraph = self.graph.subgraph(reachable)
        return self.serialize_graph(subgraph)

    def serialize_graph(self, graph: Optional[nx.DiGraph] = None) -> Dict[str, Any]:
        """
        Serialize the graph (or a subgraph) to a JSON-friendly dict.

        Returns:
            Dict with 'nodes' and 'edges' lists.
        """
        g = graph or self.graph

        nodes = [
            {"id": node, **data}
            for node, data in g.nodes(data=True)
        ]
        edges = [
            {"source": u, "target": v, **data}
            for u, v, data in g.edges(data=True)
        ]

        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": g.number_of_nodes(),
            "total_edges": g.number_of_edges(),
        }

    def _resolve_module_to_file(
        self,
        module_name: str,
        files: List[Dict[str, Any]],
    ) -> Optional[str]:
        """
        Attempt to resolve a Python module name to a file path.

        This is a simplified resolver; production would need full sys.path resolution.
        """
        # Convert module.path.name → module/path/name.py
        possible_path = module_name.replace(".", "/") + ".py"
        possible_init = module_name.replace(".", "/") + "/__init__.py"

        for f in files:
            rel = f["relative_path"].replace("\\", "/")
            if rel == possible_path or rel == possible_init:
                return f["relative_path"]

        return None
