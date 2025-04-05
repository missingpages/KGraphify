import os
import random
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase

# Load Neo4j credentials from config file
def load_neo4j_config(config_path="config/neo4j-local.txt"):
    """Load Neo4j connection details from config file"""
    config = {}
    with open(config_path, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                config[key] = value
    return config

# Initialize Neo4j connection
def get_neo4j_driver():
    """Create and return a Neo4j driver instance"""
    config = load_neo4j_config()
    uri = config.get('NEO4J_URI')
    username = config.get('NEO4J_USERNAME')
    password = config.get('NEO4J_PASSWORD')
    
    if not all([uri, username, password]):
        raise ValueError("Missing Neo4j connection details in config file")
    
    return GraphDatabase.driver(uri, auth=(username, password))

def execute_query(query, params=None):
    """Execute a Cypher query and return results"""
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run(query, params or {})
        records = [record.data() for record in result]
        return records
    
def get_schema_info():
    """List all node labels and relationship types in the database"""
    # Query for node labels
    node_query = "CALL db.labels()"
    node_labels = execute_query(node_query)
    
    # Query for relationship types
    rel_query = "CALL db.relationshipTypes()"
    rel_types = execute_query(rel_query)
    
    return {
        "node_labels": [record.get("label") for record in node_labels],
        "relationship_types": [record.get("relationshipType") for record in rel_types]
    }

def get_random_node(label: Optional[str] = None, where_condition: Optional[str] = None):
    """
    Get a random node from the database with optional filtering
    
    Args:
        label: Optional node label to filter by
        where_condition: Optional WHERE clause condition
    
    Returns:
        A random node matching the criteria
    """
    # Build the query
    if label:
        query = f"MATCH (n:{label})"
    else:
        query = "MATCH (n)"
    
    if where_condition:
        query += f" WHERE {where_condition}"
    
    # Add randomization and limit
    query += " RETURN n ORDER BY rand() LIMIT 1"
    
    result = execute_query(query)
    return result[0]['n'] if result else None

def get_outbound_connections(node_id: int):
    """
    List all outbound connections from a specific node
    
    Args:
        node_id: The internal ID of the node
    
    Returns:
        List of relationships and target nodes
    """
    query = """
    MATCH (n)-[r]->(target)
    WHERE elementId(n) = $node_id
    RETURN type(r) AS relationship_type, r AS relationship, target
    """
    return execute_query(query, {"node_id": node_id})

def get_inbound_connections(node_id: int):
    """
    List all inbound connections to a specific node
    
    Args:
        node_id: The internal ID of the node
    
    Returns:
        List of relationships and source nodes
    """
    query = """
    MATCH (source)-[r]->(n)
    WHERE elementId(n) = $node_id
    RETURN type(r) AS relationship_type, r AS relationship, source
    """
    return execute_query(query, {"node_id": node_id})

def get_related_nodes(node_id: int, relationship_type: Optional[str] = None, direction: str = "BOTH"):
    """
    Fetch nodes related to a specific node
    
    Args:
        node_id: The internal ID of the node
        relationship_type: Optional relationship type to filter by
        direction: Direction of relationship ('OUTGOING', 'INCOMING', or 'BOTH')
    
    Returns:
        List of related nodes with their relationship information
    """
    if direction.upper() == "OUTGOING":
        pattern = "(n)-[r]->(related)"
    elif direction.upper() == "INCOMING":
        pattern = "(related)-[r]->(n)"
    else:  # BOTH
        pattern = "(n)-[r]-(related)"
    
    query = f"MATCH {pattern} WHERE elementId(n) = $node_id"
    
    if relationship_type:
        query += f" AND type(r) = '{relationship_type}'"
    
    query += " RETURN related, type(r) AS relationship_type, r AS relationship"
    
    return execute_query(query, {"node_id": node_id})

def main():
    """
    Main function to demonstrate the traversal functions
    
    This function shows examples of using the graph traversal functions
    to explore nodes and their relationships in the knowledge graph.
    """
    # from db import execute_query
    
    # Example: Find a node to start with (e.g., a TOPIC node)
    print("\n🔍 Finding a sample node to start with...")
    query = "MATCH (n:TOPIC) RETURN elementId(n) AS node_id, n.TOPIC_TITLE AS title LIMIT 1"
    result = execute_query(query)
    
    if not result:
        print("No nodes found in the database. Please build the knowledge graph first.")
        return
    
    # Get the first node's ID and title
    node_id = result[0]['node_id']
    node_title = result[0]['title']
    print(f"Starting with node: {node_title} (ID: {node_id})")
    
    # Get node properties
    print("\n📋 Node properties:")
    # Get node properties by ID
    query = "MATCH (n) WHERE elementId(n) = $node_id RETURN n"
    node_info = execute_query(query, {"node_id": node_id})
    for key, value in node_info[0].items():
        print(f"  {key}: {value}")
    
    # Get outbound connections
    print("\n➡️ Outbound connections:")
    outbound = get_outbound_connections(node_id)
    for conn in outbound:
        print(f"  {conn['relationship_type']} -> {conn['target'].get('TOPIC_TITLE', 'Unknown')}")
    
    # Get inbound connections
    print("\n⬅️ Inbound connections:")
    inbound = get_inbound_connections(node_id)
    for conn in inbound:
        print(f"  {conn['source'].get('TOPIC_TITLE', 'Unknown')} -> {conn['relationship_type']}")
    
    # Get related nodes (both directions)
    print("\n🔄 All related nodes:")
    related = get_related_nodes(node_id)
    for rel in related:
        direction = "←" if rel.get('relationship_type') in [r['relationship_type'] for r in inbound] else "→"
        print(f"  {rel['relationship_type']} {direction} {rel['related'].get('TOPIC_TITLE', 'Unknown')}")
    
    # Example of filtering by relationship type
    if outbound:
        rel_type = outbound[0]['relationship_type']
        print(f"\n🔍 Nodes related by '{rel_type}':")
        filtered = get_related_nodes(node_id, relationship_type=rel_type)
        for rel in filtered:
            print(f"  {rel['related'].get('TOPIC_TITLE', 'Unknown')}")

if __name__ == "__main__":
    main()
