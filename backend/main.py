import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from openai import OpenAI
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# --- INITIALIZATION ---
load_dotenv()
st.set_page_config(layout="wide", page_title="OnlyMeta | Society Intelligence", page_icon="🕸️")

# Custom CSS for a modern look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTextInput { border-radius: 10px; }
    .answer-box { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 5px solid #4bafff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #1f1f1f;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. DATA ENGINE ---
@st.cache_resource
def load_unified_graph():
    G = nx.MultiDiGraph()
    # Adjust path if your folder is named differently
    graph_folder = Path("graph_data") 
    
    if not graph_folder.exists():
        return G

    for file_path in graph_folder.glob("*.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                triplets = data if isinstance(data, list) else data.get('triplets', [])
                for t in triplets:
                    s = str(t.get('subject') or t.get('entity1') or "Unknown")
                    o = str(t.get('object') or t.get('entity2') or "Unknown")
                    p = str(t.get('predicate') or "related_to")
                    G.add_edge(s, o, predicate=p, origin=file_path.name)
        except Exception:
            continue
    return G

G = load_unified_graph()

# --- 2. AI CONFIGURATION ---
api_key = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "OnlyMeta Graph Hub",
    }
)

# --- 3. UI LAYOUT ---
st.title("🕸️ Society Knowledge Intelligence")
st.markdown("Query the collective knowledge of all campus societies.")

# Sidebar Stats
with st.sidebar:
    st.header("Graph Statistics")
    st.metric("Total Entities", len(G.nodes()))
    st.metric("Relationships", len(G.edges()))
    st.markdown("---")
    st.info("The AI traverses the graph to find hidden connections between societies, members, and projects.")

# Main Search
query = st.text_input("Enter your query:", placeholder="Who is the head of DevSoc? / What projects does Robotics Club do?")

if query:
    if not api_key:
        st.error("API Key not found! Please set OPENROUTER_API_KEY in your .env file.")
        st.stop()

    with st.spinner("AI is analyzing the graph..."):
        # STEP 1: Identify Starting Node
        node_sample = list(G.nodes())[:100]
        try:
            res_node = client.chat.completions.create(
                model="xiaomi/mimo-v2-flash:free",
                messages=[
                    {"role": "system", "content": "You are a graph expert. Extract the single most important entity name from the user's query. Return ONLY the name."},
                    {"role": "user", "content": f"Query: {query}. Possible matches: {node_sample}"}
                ]
            )
            start_node = res_node.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"AI Error: {e}")
            st.stop()

    # Fuzzy matching if exact node not found
    if not G.has_node(start_node):
        potential_matches = [n for n in G.nodes() if start_node.lower() in n.lower()]
        if potential_matches:
            start_node = potential_matches[0]

    if G.has_node(start_node):
        # STEP 2: Traversal (Ego Graph)
        # radius=1 finds direct neighbors. Increase to 2 for deeper traversal.
        sub = nx.ego_graph(G, start_node, radius=1)
        
        # Extract facts for the second AI call
        facts = [f"{u} {d['predicate']} {v}" for u, v, d in sub.edges(data=True)]
        context = "\n".join(facts)

        # STEP 3: Generate Answer based on Graph Facts
        try:
            res_ans = client.chat.completions.create(
                model="xiaomi/mimo-v2-flash:free",
                messages=[
                    {"role": "system", "content": "Answer the user question using ONLY the provided graph data. Be concise and professional."},
                    {"role": "user", "content": f"Question: {query}\n\nData Found in Graph:\n{context}"}
                ]
            )
            answer = res_ans.choices[0].message.content
        except Exception as e:
            answer = f"Found the data visually, but could not generate text answer: {e}"

        # --- UI DISPLAY ---
        st.markdown(f'<div class="answer-box"><b>AI Answer:</b><br>{answer}</div>', unsafe_allow_html=True)
        
        st.markdown("### 🗺️ Visual Context")
        col1, col2 = st.columns([3, 1])

        with col1:
            # Styled Pyvis Graph
            net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#333333", directed=True)
            for u, v, data in sub.edges(data=True):
                # Color code the starting node
                u_color = "#ff4b4b" if u == start_node else "#4bafff"
                net.add_node(u, label=u, color=u_color, size=30 if u == start_node else 25, font={'weight': 'bold'})
                net.add_node(v, label=v, color="#97c2fc", size=20)
                net.add_edge(u, v, label=data['predicate'], color="#cccccc", smooth={'type': 'curvedCW'})
            
            net.set_options('{"physics": {"barnesHut": {"gravitationalConstant": -30000, "springLength": 200}}}')
            net.save_graph("subgraph.html")
            with open("subgraph.html", 'r', encoding='utf-8') as f:
                components.html(f.read(), height=650)

        with col2:
            st.write("**Related Links**")
            for f in facts[:15]: # Limit list for UI cleanliness
                st.caption(f)
            if len(facts) > 15:
                st.write(f"...and {len(facts)-15} more.")
    else:
        st.warning(f"Could not find an entity named '{start_node}' in the database.")