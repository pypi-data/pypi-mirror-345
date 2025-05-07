# prasanth.py
from prasanth.neo4j_schema import extract_neo4j_schema_to_txt

def hello():
    return "Hello from Prasanth!"

def addition(a, b):
    return a + b

def get_graph_schema(uri, user, password, database, output_file_path):
    extract_neo4j_schema_to_txt(uri, user, password, database, output_file_path)
    return f"Schema saved to {output_file_path}"
