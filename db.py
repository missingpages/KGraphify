import neo4j
from neo4j import GraphDatabase

def load_neo4j_credentials():
    """Load Neo4j credentials from file"""
    print("Loading Neo4j credentials...")
    credentials = {}
    try:
        with open('neo4j-local.txt', 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                credentials[key] = value
        print("✓ Credentials loaded successfully")
        return credentials
    except FileNotFoundError:
        print("❌ Error: neo4j-local.txt file not found")
        raise
    except Exception as e:
        print(f"❌ Error loading credentials: {str(e)}")
        raise

def get_neo4j_driver():
    """Create and return Neo4j driver using credentials"""
    print("Initializing Neo4j connection...")
    try:
        credentials = load_neo4j_credentials()
        driver = neo4j.GraphDatabase.driver(
            credentials['NEO4J_URI'],
            auth=neo4j.basic_auth(credentials['NEO4J_USERNAME'], credentials['NEO4J_PASSWORD'])
        )
        print("✓ Neo4j connection established")
        return driver
    except Exception as e:
        print(f"❌ Error connecting to Neo4j: {str(e)}")
        raise

def execute_query(query):
    """Execute Neo4j query using driver"""
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run(query)
        records = [record for record in result]
        return records