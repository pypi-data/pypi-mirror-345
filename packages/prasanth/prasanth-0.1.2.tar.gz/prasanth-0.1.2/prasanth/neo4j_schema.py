from neo4j import GraphDatabase

def extract_neo4j_schema_to_txt(uri, user, password, database, output_file_path):
    driver = GraphDatabase.driver(uri, auth=(user, password))

    def fetch_schema(tx):
        result = tx.run("CALL db.schema.visualization()")
        return result.single()

    with driver.session(database=database) as session:
        schema = session.read_transaction(fetch_schema)

    nodes = schema["nodes"]
    relationships = schema["relationships"]

    lines = []
    lines.append("=== Neo4j Schema ===\n")

    lines.append("Nodes:\n")
    for node in nodes:
        labels = node["labels"]
        lines.append(f"  - {'::'.join(labels)}")

    lines.append("\nRelationships:\n")
    for rel in relationships:
        start = "::".join(rel["start"]["labels"])
        end = "::".join(rel["end"]["labels"])
        rtype = rel["type"]
        lines.append(f"  - ({start}) -[:{rtype}]-> ({end})")

    # Save to file
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    driver.close()
    print(f"Schema saved to: {output_file_path}")
