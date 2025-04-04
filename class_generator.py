
import os
import fitz
from langchain_core.output_parsers import JsonOutputParser
from openai import OpenAI
client = OpenAI()
from typing import Optional
import yaml
import sys
from pydantic import BaseModel,Field,create_model 
from langchain_openai import ChatOpenAI
from typing import Union

class ENTITY_NODE(BaseModel):
    entity_label:str = Field(description = "Type of entity extracted from the data For eg. PERSON,OBJECT,PLACE etc")
    entity_name:str = Field(description = "Name of the entity extracted For eg. Shakespear, London etc")   
        
class ENTITY(BaseModel):
    entity:ENTITY_NODE = Field(description="entity extracted from data")
              
class RELATION(BaseModel):
    from_entity:ENTITY_NODE = Field(description = "Entity from which the relationship exists")
    to_entity:ENTITY_NODE = Field(description = "Entity to which the relationship points to")
    relation_type:str = Field(description="Relation between from and to enitites.Must be in ONE word.For eg: HAS,INCLUDES, OWNS, VISITS etc")
                                                             
class FREE_FLOW_GRAPH(BaseModel):
    entities:list[ENTITY] = Field(description="List of all entities extracted from data")
    relations:list[RELATION] = Field(description="Captures all relationships between all entities captured from data")
    
def create_freeflow_graph_model():
    return FREE_FLOW_GRAPH

def create_entity_class(all_defined_entities:dict):
    ENTITY_CLASS_FIELDS = {}   
    lst = [entity for entity in list(all_defined_entities.values())]
    ENTITY_CLASS_FIELDS['entity'] = (Union[tuple(lst)],Field(description="entity extracted from data"))
    ENTITY_CLASS = create_model(
                'ENTITY', **ENTITY_CLASS_FIELDS
            )
    return ENTITY_CLASS

def str_to_class(datatype):
    return getattr(sys.modules[__name__], datatype)


def create_relation_class(all_defined_relations):
    REL_CLASS_FIELDS = {}
    REL_CLASS_FIELDS['from_entity'] = (ENTITY,Field(description = "Entity from which the relationship exists"))
    REL_CLASS_FIELDS['to_entity'] = (ENTITY, Field(description = "Entity to which the relationship points to"))
    REL_CLASS_FIELDS['relation_type'] = (str,Field(description = "Relation between from and to enitites.For eg: HAS,INCLUDES, OWNS, VISITS etc"))
    RELATION_CLASS = create_model('RELATION' , **REL_CLASS_FIELDS)
    return RELATION_CLASS
    
def create_dyn_model_with_entities(entities,relations=None):
    all_defined_entities = {}
    for entity in entities:
        properties = entity['properties']
        fields = {}
        for prop in properties:
            fields[prop['name']] = (eval(prop['type']), Field(description=prop['description']))
        fields['entity_label'] = (str, entity['name'])
        print(f"creating model for {entity}")    
        entity_class = create_model(
                entity['name'], **fields
            )# creates individual defined entities
        all_defined_entities[entity['name']] = entity_class
        
    
    ENTITY_CLASS = create_entity_class(all_defined_entities)
    
    if relations is None:
        RELATION_CLASS = create_relation_class(all_defined_relations)
    else:
        all_defined_relations= {}
        for rel in relations:
            properties = rel['properties']
            print(properties)
            fields = {}
            if not properties['from'] in all_defined_entities.keys() or not properties['to'] in all_defined_entities.keys():
                print("entities not present!")
                return None

            fields['from_entity'] = (all_defined_entities[properties['from']],Field(description = "Entity from which the relationship exists"))
            fields['to_entity'] = (all_defined_entities[properties['to']],Field(description = "Entity to which the relationship exists"))
            fields['relation_type'] = (str,rel['name'])
            relation_class = create_model(rel['name'],**fields) 
            all_defined_relations[rel['name']] = relation_class
            
        RELATION_CLASS = Union[tuple([r for r in all_defined_relations.values()])]
    
    print(ENTITY_CLASS.model_json_schema())
    graph_fields = {}
    graph_fields['entities'] = (list[ENTITY_CLASS],Field(description="List of all entities extracted from data"))
    graph_fields['relations'] = (list[RELATION_CLASS],Field(description="Captures all relationships between all entities captured from data"))
    GRAPH_CLASS =  create_model('GRAPH' , **graph_fields)   
#     GRAPH_CLASS.model_rebuild()
    return GRAPH_CLASS
   
    
   
    
def create_structured_output_model(entities,relations):
    if entities is None and relations is None:
        structured_model = create_freeflow_graph_model()
    else:
        structured_model = create_dyn_model_with_entities(entities,relations)
    return structured_model
    