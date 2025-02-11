from pydantic import BaseModel, Field, create_model
import yaml
from typing import Optional, Dict, Any

def load_schema(yaml_file):
    with open(yaml_file, 'r') as file:
        yaml_data = yaml.safe_load(file)
    return yaml_data

def read_entities(schema):
    entities = schema['graph']['ENTITIES']
    return entities
    
def read_relations(schema):
    if 'RELATIONS' not in schema['graph']:
        return None
    relations = schema['graph']['RELATIONS']
    return relations



