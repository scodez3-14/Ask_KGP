import os
import json
import networkx as nx
from pathlib import Path

# 1. SETUP PATHS: Looks for 'graph_data' folder inside the 'backend' folder
SCRIPT_DIR = Path(__file__).resolve().parent
GRAPH_DIR = SCRIPT_DIR / "graph_data"

def flatten_node(node_value):
    """
    Ensures the node is a string. If it's a dict, extracts 'name' or 'text'.
    This prevents 'unhashable type: dict' errors.
    """
    if isinstance(node_value, dict):
        # Try common keys LLMs use for entity names
        return node_value.get('name') or node_value.get('text') or node_value.get('entity') or str(node_value)
    return str(node_value) if node_value is not None else None

def create_society_graph():
    # MultiDiGraph allows multiple edges (predicates) between nodes
    G = nx.MultiDiGraph()
    
    if not GRAPH_DIR.exists():
        print(f"Error: Folder not found at {GRAPH_DIR}")
        return G

    files = list(GRAPH_DIR.glob("*.json"))
    print(f"Found {len(files)} JSON files in {GRAPH_DIR}")

    for file_path in files:
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                
                # Check if JSON is a list or a dict containing a list
                triplets = data if isinstance(data, list) else data.get('triplets', [])
                
                for t in triplets:
                    # 1. Extract raw values (allowing for various naming conventions)
                    s_raw = t.get('subject') or t.get('Subject') or t.get('entity1')
                    o_raw = t.get('object') or t.get('Object') or t.get('entity2')
                    p_raw = t.get('predicate') or t.get('Predicate') or "related_to"
                    
                    # 2. Flatten nodes to strings to avoid "Unhashable type: dict"
                    s = flatten_node(s_raw)
                    o = flatten_node(o_raw)
                    p=flatten_node(p_raw)
                    src_raw=t.get('source_id') or file_path.name
                    src=flatten_node(src_raw)
                    
                    # 3. Add to graph if data is valid
                    if s and o:
                        G.add_edge(s, o, predicate=p, source=src)
                        
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"Skipping malformed file {file_path.name}: {e}")
                
    return G

if __name__ == "__main__":
    # Create the graph
    G = create_society_graph()
    
    # Summary
    print(f"\n--- Graph Created Successfully ---")
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")

    # Save as a single GraphML file for later use
    output_path = SCRIPT_DIR / "full_graph.graphml"
    nx.write_graphml(G, output_path)
    print(f"Saved merged graph to: {output_path}")

    # Example Query
    print("\nSample connections for 'IIT Kharagpur':")
    if G.has_node("IIT Kharagpur"):
        for _, neighbor, attr in G.out_edges("IIT Kharagpur", data=True):
            print(f"  - [{attr['predicate']}] -> {neighbor}")