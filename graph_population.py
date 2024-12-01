from config.neo4j_config import get_driver
import pandas as pd

driver = get_driver()

def create_knowledge_graph(data):
    """Populate the Neo4j database with the knowledge graph."""
    with driver.session() as session:
        for _, row in data.iterrows():
            # Skip rows with missing country names or other critical fields
            if pd.isna(row["Country"]) or pd.isna(row["Capital/Major City"]) or pd.isna(row["Largest city"]):
                continue

            # Use a default value for missing Official language
            official_language = row["Official language"] if pd.notna(row["Official language"]) else "Unknown"
            
            # Check for NaN or empty currency code
            currency_code = row["Currency-Code"] if pd.notna(row["Currency-Code"]) else "UNKNOWN"

            # Create nodes for Country, City, Currency, and Language
            session.run("MERGE (c:Country {name: $name})", name=row["Country"])
            session.run("MERGE (capital_city:City {name: $name})", name=row["Capital/Major City"])
            session.run("MERGE (largest_city:City {name: $name})", name=row["Largest city"])
            session.run("MERGE (currency:Currency {code: $code})", code=currency_code)
            session.run("MERGE (lang:Language {name: $name})", name=official_language)

            # Create relationships
            session.run("""
                MATCH (country:Country {name: $country}), (city:City {name: $capital})
                MERGE (country)-[:LOCATED_AT]->(city)
            """, country=row["Country"], capital=row["Capital/Major City"])

            session.run("""
                MATCH (country:Country {name: $country}), (city:City {name: $largest})
                MERGE (country)-[:LARGEST_CITY_IN]->(city)
            """, country=row["Country"], largest=row["Largest city"])

            session.run("""
                MATCH (country:Country {name: $country}), (currency:Currency {code: $currency})
                MERGE (country)-[:HAS_CURRENCY]->(currency)
            """, country=row["Country"], currency=currency_code)

            session.run("""
                MATCH (country:Country {name: $country}), (lang:Language {name: $language})
                MERGE (country)-[:SPEAKS]->(lang)
            """, country=row["Country"], language=official_language)
