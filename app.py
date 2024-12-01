import streamlit as st
import pandas as pd
import google.generativeai as genai
from src.schema_inference import infer_schema
from src.graph_population import create_knowledge_graph
from neo4j import GraphDatabase
import networkx as nx
from pyvis.network import Network

# Set your Gemini API key
genai.configure(api_key="AIzaSyCtwToVA60UQpJpa1BrHHGxxoxcoSNBBbM")

# Neo4j Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"

# Function to get the Neo4j driver
def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# Connect to Neo4j
driver = get_driver()

# Function to query the Neo4j graph database
def query_graph(cypher_query):
    with driver.session() as session:
        result = session.run(cypher_query)
        return result.data()

# Function to visualize the graph using Pyvis
def visualize_graph(data):
    if not data:
        st.error("No data available to visualize.")
        return None

    G = nx.Graph()
    for record in data:
        if 'p' in record:
            path = record['p']
            for node in path.nodes:
                G.add_node(node['name'], label=node.get('name', 'Node'))
            for rel in path.relationships:
                G.add_edge(rel.start_node['name'], rel.end_node['name'], label=rel.type)

    net = Network(height="600px", width="100%", bgcolor="#f7f9fa", font_color="black")
    net.from_nx(G)
    return net

# Refine schema using Gemini API
def refine_schema(entities, relationships):
    prompt = f"""
    Detected Entities: {entities}
    Detected Relationships: {relationships}
    Please suggest improvements or additions to the schema.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

# Streamlit App Layout and Styling
st.set_page_config(page_title="Knowledge Graph Builder", page_icon="🌐", layout="wide")

st.title("🌐 Automated Knowledge Graph Builder and Visualizer")
st.markdown(
    """
    Build and visualize knowledge graphs seamlessly using Neo4j and Google's Generative AI.
    """
)

# Sidebar for navigation
st.sidebar.header("📂 File Operations")

# Add file uploader to replace hardcoded file paths
uploaded_file = st.sidebar.file_uploader(
    "Upload Dataset (CSV format only)", type=["csv"]
)

# Load Dataset
if uploaded_file:
    try:
        data = pd.read_csv(uploaded_file)
        st.subheader("📊 Dataset Preview")
        st.dataframe(data.head(), use_container_width=True)
    except Exception as e:
        st.sidebar.error(f"Error loading dataset: {e}")
        st.stop()
else:
    st.sidebar.info("Please upload a dataset to proceed.")
    st.stop()

# Schema Inference
if 'entities' not in st.session_state:
    st.session_state.entities = None
if 'relationships' not in st.session_state:
    st.session_state.relationships = None
if 'properties' not in st.session_state:
    st.session_state.properties = None

st.sidebar.markdown("### 🛠 Schema Operations")
if st.sidebar.button("Infer Schema"):
    try:
        entities, relationships, properties = infer_schema(data)
        st.session_state.entities = entities
        st.session_state.relationships = relationships
        st.session_state.properties = properties
        st.subheader("📋 Detected Schema")
        st.write("**Entities**", st.session_state.entities)
        st.write("**Relationships**", st.session_state.relationships)
        st.write("**Properties**", st.session_state.properties)
    except Exception as e:
        st.error(f"Error inferring schema: {e}")

# Add predefined queries to the list
predefined_queries = [
    "MATCH (c:Country) RETURN c.name LIMIT 10",
    "MATCH (c:Country)-[:HAS_CURRENCY]->(currency:Currency) RETURN c.name, currency.code LIMIT 10",
    "MATCH (c:Country)-[:LARGEST_CITY_IN]->(city:City) RETURN c.name, city.name LIMIT 10",
    "MATCH (c:Country)-[:SPEAKS]->(lang:Language) RETURN c.name, lang.name LIMIT 10",
    "MATCH (c:Country)-[:LOCATED_AT]->(city:City) RETURN c.name, city.name LIMIT 10",
    "MATCH (city:City)-[r]->(c:Country) RETURN city.name, type(r), c.name LIMIT 10",
    "MATCH (c:Country)-[:HAS_CURRENCY]->(currency:Currency) WHERE currency.code = 'USD' RETURN c.name",
    "MATCH (lang:Language)<-[:SPEAKS]-(c:Country) RETURN lang.name, c.name LIMIT 10",
    "MATCH p=(city:City)-[r]->() RETURN p LIMIT 25",
    "MATCH (c:Country)-[:LARGEST_CITY_IN]->(city:City) WHERE city.population > 1000000 RETURN c.name, city.name",
    "MATCH (c:Country)-[:LOCATED_AT]->(city:City) RETURN c.name, city.latitude, city.longitude LIMIT 10",
    "MATCH (currency:Currency)<-[:HAS_CURRENCY]-(c:Country) RETURN currency.code, c.name LIMIT 10"
]

# Sidebar for Query Selection
st.sidebar.markdown("### 🔍 Query Execution")
query_option = st.sidebar.selectbox(
    "Choose a query:", 
    ["Select a predefined query"] + predefined_queries
)
custom_query = ""
if query_option == "Select a predefined query":
    custom_query = st.sidebar.text_area("Write your query", height=100)

if st.sidebar.button("Run Query"):
    query = query_option if query_option != "Select a predefined query" else custom_query
    if query:
        try:
            results = query_graph(query)
            if results:
                st.subheader("🛠 Query Results")
                st.json(results)
                net = visualize_graph(results)
                if net:
                    net.show("graph.html")
                    st.components.v1.html(open("graph.html", "r").read(), height=600)
            else:
                st.info("No results found.")
        except Exception as e:
            st.error(f"Error running query: {e}")
    else:
        st.warning("Enter a Cypher query to run.")

# Refine schema options
st.sidebar.markdown("### 🔧 Refine Schema")
refine_option = st.sidebar.radio(
    "How would you like to refine the schema?",
    ["Let AI Suggest Improvements", "Write Your Own Relationship"]
)

if refine_option == "Let AI Suggest Improvements":
    if st.session_state.entities and st.session_state.relationships:
        try:
            refined_schema = refine_schema(st.session_state.entities, st.session_state.relationships)
            st.subheader("🔍 Refined Schema")
            st.write(refined_schema)
        except Exception as e:
            st.error(f"Error refining schema: {e}")
    else:
        st.warning("Please infer the schema first.")

elif refine_option == "Write Your Own Relationship":
    relationship_input = st.text_area("Enter your custom relationship", height=100)
    if st.button("Submit Custom Relationship"):
        if relationship_input:
            st.write("**Custom Relationship**")
            st.write(relationship_input)
        else:
            st.warning("Please enter a custom relationship.")

# Populate Knowledge Graph
if st.sidebar.button("Populate Knowledge Graph"):
    try:
        create_knowledge_graph(data)
        st.success("🎉 Knowledge graph populated successfully!")
    except Exception as e:
        st.error(f"Error populating knowledge graph: {e}")
