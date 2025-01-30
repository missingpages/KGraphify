from typing import get_origin,get_args,Union
import inspect
from pydantic import BaseModel
import pydantic
import neo4j
from db import *


def get_relation_from_triplets(parent,child):
    rel = None
    triplets = extract_triplets('test.yaml')
    for triplet in triplets:
        if triplet[0]==parent and triplet[1]==child:
            rel = triplet[2] 
    return rel    

def convert_dict_to_str(node_dict):
    props_list = []
    for k,v in node_dict.items():
        
            props = f"{k}:'{v}'"
            props_list.append(props)
            
    attrs = ','.join(props_list)
    return attrs


def buildKG(node_key,node_values,parent=None):
    
    
    node_props = {}
    query = f"MERGE (node:{node_key}"
    props_list = []
    
    # process node properties
    for k,v in node_values.items():
        if  k != 'includes':
            print(k)
            node_props[k]=v
            props = f"{k}:'{v}'"
            props_list.append(props)
            
    attrs = ','.join(props_list)
    query_with_attrs = query + f"{{{attrs} }} )"
    print(query_with_attrs)        
    print(f"parent node is {parent}")
    execute_query(query_with_attrs)
    
    if parent:
        query_with_rel = f"MATCH (p:{parent[0]} {{ {convert_dict_to_str(parent[1])}}}), (c:{node_key} {{ {convert_dict_to_str(node_props)}}}) WITH p,c MERGE (p)-[:{get_relation_from_triplets(parent[0],node_key)}]->(c)"
        print(query_with_rel)
        execute_query(query_with_rel)
    
    # process includes  
    
    for k,v in node_values.items():
        if  k == 'includes':
            
            parent_node = (node_key,node_props)
            for child in v: #items in 'includes' list
                print(f"child in includes list:{child}")
                for k,v in child.items():
                    child_nodes = child[k]
                    if type(child_nodes) is list:
                        for obj in child_nodes:
                            buildKG(k,obj,parent_node)
                    else:
                        buildKG(k,child_nodes,parent_node)
                            

    #                 print(k,v)
                pass
    