import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()

# --- INITIALIZE OPENROUTER CLIENT ---
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
  default_headers={
    "HTTP-Referer": "http://localhost:8501", # Required by OpenRouter
    "X-Title": "Society Graph App",
  }
)


@st.cache_resource
def get_graph():
    return nx.read_graphml("full_graph.graphml")

G = get_graph()

st.title("Society Intelligence Hub")

# --- UI ---
user_query = st.text_input("What would you like to know?", placeholder="e.g., Which projects are linked to the Robotics Club?")

if user_query:
    with st.spinner("AI is analyzing the graph..."):
        # STEP 1: Use OpenRouter to find the starting node
        # We pass a sample of node names to help the AI map the query to the data
        nodes_list = list(G.nodes())[:100] # Give a sample of 100 nodes
        
        response = client.chat.completions.create(
          model="google/gemini-2.0-flash-001", # You can use any model from OpenRouter
          messages=[
            {"role": "system", "content": f"You are a Graph Database assistant. Identify the most relevant node from this list for the user's question. Return ONLY the node name. Nodes: {nodes_list}"},
            {"role": "user", "content": user_query}
          ]
        )
        
        target_node = response.choices[0].message.content.strip()

    # STEP 2: TRAVERSAL
    if G.has_node(target_node):
        st.success(f"AI identified focal point: **{target_node}**")
        
        # Travel 2 hops from the identified node
        subgraph = nx.ego_graph(G, target_node, radius=2)
        
        # STEP 3: VISUALIZE
        vis_net = Network(height="500px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
        
        # Collapse MultiDiGraph to DiGraph for Pyvis compatibility
        simple_graph = nx.DiGraph(subgraph)
        vis_net.from_nx(simple_graph)
        
        # Save and Render
        vis_net.save_graph("temp_query.html")
        with open("temp_query.html", 'r', encoding='utf-8') as f:
            components.html(f.read(), height=550)
            
        # Display the text-based answer logic
        with st.expander("Show detailed traversal path"):
            for u, v, d in subgraph.edges(data=True):
                st.write(f"Found: **{u}** --({d['predicate']})--> **{v}**")
    else:
        st.warning(f"AI suggested node '{target_node}', but it doesn't exist in your JSON data. Try being more specific.")