"""Alt network graph generation."""

from typing import List, Dict, Any
from sentinel.models.analysis_result import AltRelationship


class GraphGenerator:
    """Generates graph data for visualizing alt relationships."""
    
    def generate(
        self,
        character_id: int,
        character_name: str,
        potential_alts: List[AltRelationship]
    ) -> Dict[str, Any]:
        """
        Generate graph data structure for alt network visualization.
        
        Returns a graph in a format suitable for networkx or other graph libraries.
        """
        # Create nodes and edges for graph visualization
        nodes = []
        edges = []
        
        # Add the main character as the center node
        nodes.append({
            "id": character_id,
            "label": character_name,
            "type": "main",
            "size": 20
        })
        
        # Add potential alts as connected nodes
        for alt in potential_alts:
            nodes.append({
                "id": alt.character_id,
                "label": alt.character_name,
                "type": "potential_alt",
                "size": 10 + (alt.probability * 10)  # Size based on probability
            })
            
            edges.append({
                "source": character_id,
                "target": alt.character_id,
                "weight": alt.probability,
                "label": f"{alt.probability:.0%}",
                "evidence": alt.evidence
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "center_character": character_id,
                "total_potential_alts": len(potential_alts),
                "high_probability_count": len([a for a in potential_alts if a.probability > 0.6])
            }
        }
    
    def generate_networkx_graph(
        self,
        character_id: int,
        character_name: str,
        potential_alts: List[AltRelationship]
    ):
        """
        Generate a networkx Graph object for visualization.
        
        Requires networkx to be installed.
        """
        try:
            import networkx as nx
        except ImportError:
            raise ImportError("networkx is required for graph generation. Install with: pip install networkx")
        
        G = nx.Graph()
        
        # Add main character node
        G.add_node(character_id, label=character_name, node_type="main")
        
        # Add alt nodes and edges
        for alt in potential_alts:
            G.add_node(alt.character_id, label=alt.character_name, node_type="potential_alt")
            G.add_edge(
                character_id, 
                alt.character_id, 
                weight=alt.probability,
                evidence=alt.evidence
            )
        
        return G
    
    def visualize_graph(self, graph_data: Dict[str, Any], output_path: str = None):
        """
        Create a visual representation of the alt network graph.
        
        Args:
            graph_data: Graph data from generate()
            output_path: Optional path to save the visualization
        """
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("networkx and matplotlib required. Install with: pip install networkx matplotlib")
        
        # Create graph
        G = nx.Graph()
        
        # Add nodes
        for node in graph_data["nodes"]:
            G.add_node(node["id"], **node)
        
        # Add edges
        for edge in graph_data["edges"]:
            G.add_edge(edge["source"], edge["target"], **edge)
        
        # Create visualization
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Draw nodes
        main_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "main"]
        alt_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "potential_alt"]
        
        nx.draw_networkx_nodes(G, pos, nodelist=main_nodes, node_color='red', 
                              node_size=1000, label='Main Character')
        nx.draw_networkx_nodes(G, pos, nodelist=alt_nodes, node_color='lightblue', 
                              node_size=500, label='Potential Alt')
        
        # Draw edges with varying thickness based on probability
        edges = G.edges()
        weights = [G[u][v]['weight'] * 5 for u, v in edges]
        nx.draw_networkx_edges(G, pos, width=weights, alpha=0.5)
        
        # Draw labels
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels, font_size=10)
        
        # Draw edge labels (probabilities)
        edge_labels = {(u, v): f"{d['weight']:.0%}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)
        
        plt.title("Alt Relationship Network")
        plt.legend()
        plt.axis('off')
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
