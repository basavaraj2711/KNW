from neo4j import GraphDatabase

# For local Neo4j setup (default configuration)
NEO4J_URI = "bolt://localhost:7687"  # Ensure Neo4j is running on this port
NEO4J_USERNAME = "neo4j"  # Default username
NEO4J_PASSWORD = "password"  # Default password (change it if you've updated)

def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

