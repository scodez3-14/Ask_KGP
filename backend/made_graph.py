import json
from pyvis.network import Network

def build_clean_graph(input_json):
    net = Network(height="850px", width="100%", bgcolor="#ffffff", font_color="#333333", directed=True, cdn_resources='remote')

    with open(input_json, 'r') as f:
        data = json.load(f)

    for entry in data:
        s = str(entry.get('subject', 'Unknown'))
        p = str(entry.get('predicate', ''))
        o = str(entry.get('object', 'Unknown'))

        # STYLING NODES: Large, bold, and distinct
        net.add_node(s, label=s, size=25, font={'size': 18, 'face': 'Arial', 'multi': True, 'weight': 'bold'}, color="#4bafff")
        net.add_node(o, label=o, size=20, font={'size': 14, 'face': 'Arial'}, color="#97c2fc")

        # STYLING EDGES: Smaller text, curved lines to avoid overlapping nodes
        net.add_edge(s, o, 
                     label=p, 
                     arrowStrikethrough=False,
                     font={'size': 10, 'color': '#888888', 'align': 'horizontal', 'background': 'white'}, 
                     color={'color': '#cccccc', 'highlight': '#4bafff'},
                     smooth={'type': 'curvedCW', 'roundness': 0.2}) # Curves the line to prevent overlap

    # PHYSICS & LAYOUT ENGINE
    # This configuration forces nodes to push away from each other (avoiding label overlap)
    net.set_options("""
    var options = {
      "nodes": {
        "margin": 10
      },
      "edges": {
        "font": {
          "strokeWidth": 2,
          "strokeColor": "#ffffff"
        }
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -30000,
          "centralGravity": 0.3,
          "springLength": 200,
          "springConstant": 0.05,
          "avoidOverlap": 1
        },
        "minVelocity": 0.75
      }
    }
    """)

    net.save_graph("clean_knowledge_graph.html")

build_clean_graph('graph_data/Developers%27_Society.json')