def infer_schema(data):
    """
    Infer schema with expanded entities and relationships based on the dataset.
    """
    # Core entities
    entities = [
        "Country", "Capital/Major City", "Largest City", "Currency_Code", "Official Language"
    ]

    # Initial relationships
    relationships = [
        {"type": "located_at", "from": "Country", "to": "Capital/Major City"},
        {"type": "largest_city_in", "from": "Country", "to": "Largest City"},
        {"type": "uses_currency", "from": "Country", "to": "Currency_Code"},
        {"type": "speaks_language", "from": "Country", "to": "Official Language"},
    ]

    # Adding specified relationships
    additional_relationships = [
        {"type": "has_population_density", "from": "Country", "to": "Density"},
        {"type": "has_abbreviation", "from": "Country", "to": "Abbreviation"},
        {"type": "has_land_area", "from": "Country", "to": "Land Area"},
        {"type": "has_armed_forces", "from": "Country", "to": "Armed Forces Size"},
        {"type": "has_birth_rate", "from": "Country", "to": "Birth Rate"},
        {"type": "has_calling_code", "from": "Country", "to": "Calling Code"},
        {"type": "has_urban_population", "from": "Country", "to": "Urban Population"},
        {"type": "located_at_coordinates", "from": "Country", "to": ["Latitude", "Longitude"]},
    ]
    relationships.extend(additional_relationships)

    # Adding any additional columns as generic properties
    properties = {}
    for column in data.columns:
        if column not in entities and column not in [rel["to"] for rel in relationships]:
            entities.append(column)
            # Normalize column names to create relationship types
            normalized_column = (
                column.lower()
                .replace(' ', '_')
                .replace(':', '')
                .replace('\n', '')
                .replace('(', '')
                .replace(')', '')
            )
            relationship_type = f"has_{normalized_column}"
            relationships.append({"type": relationship_type, "from": "Country", "to": column})
        else:
            # Add to properties dictionary
            properties[column] = "property"

    return entities, relationships, properties
