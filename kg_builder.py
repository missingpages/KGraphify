from db import execute_query



def convert_dict_to_str(node_dict):
    props_list = []
    for k,v in node_dict.items():
            v = v.replace("'", "`")
            props = f"{k}:'{v}'"
            props_list.append(props)
            
    attrs = ','.join(props_list)
    return attrs
    

def create_graph_nodes(entity_name, props):
    query = f""" MERGE (n:{entity_name} {{{convert_dict_to_str(props)}}}) RETURN n"""
    print(query)
    execute_query(query)


def create_nodes(entity_nodes,global_config):
    for entity in entity_nodes:
        node = entity['entity']
        node_label = entity['entity']['entity_label']
        # Copy global_config key-values to node dict
        for key, value in global_config.items():
            node[key] = value
        print(node_label)
        create_graph_nodes(node_label,node)

def create_graph_relations(rel,global_config):
    from_entity_props = rel['from_entity']
    print(from_entity_props)
    from_node_entity = from_entity_props['entity_label']
    
    to_entity_props = rel['to_entity']
    to_node_entity = to_entity_props['entity_label']
    
    rel_type = rel['relation_type']
    
    query = f"""MATCH (p:{from_node_entity}{{{convert_dict_to_str(from_entity_props)}}}), (c:{to_node_entity}{{{convert_dict_to_str(to_entity_props)}}})
    WITH p,c
    MERGE (p)-[:{rel_type}{{{convert_dict_to_str(global_config)}}}]->(c)"""
    print(f"Creating relation from {from_node_entity} to {to_node_entity} as {rel_type}")
    execute_query(query)

def create_relations(relations,global_config):
    for rel in relations:
        create_graph_relations(rel,global_config)