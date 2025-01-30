from pydantic import BaseModel, Field, create_model
import yaml
from typing import Optional, Dict, Any


with open('test.yaml', 'r') as file:
    yaml_data = yaml.safe_load(file)


root_concepts = yaml_data['concepts']['includes']
# print("root concepts #######",root_concepts)

def get_leaf_concept(included_concepts):
    if 'includes' in included_concepts:
        print("--------------------------------")
        print("included concepts *******",included_concepts)
        child_concepts = included_concepts['includes']
        fields = {}
        for child_concept in child_concepts:
            dyn_model_dict =  get_leaf_concept(child_concept)
            
            included_class = dyn_model_dict[child_concept['name']]
            if child_concept.get('relation') == 'one_to_many':
                # plural_name = f"{child_concept['name']}S"  # Dynamic plural name
                fields[child_concept['name']] = (Optional[list[included_class]], 
                    Field(description=child_concept['description'], 
                            default=['NULL']))
            else:
                fields[child_concept['name']] = (included_class, 
                    Field(description=child_concept['description']))
            
            

        # fields = {}
        if 'contains' in included_concepts:
                for field in included_concepts['contains']:
                    fields[field['name']] = (field['type'], Field(description=field['description']))
        combined_fields = {**fields}            
        print("fields #######",combined_fields)
        dynamic_model = create_model(
                included_concepts['name'], **combined_fields
            )
        print("dyn model #######",dynamic_model)
        return {included_concepts['name']: dynamic_model}
    else:
       
        print("child concept:",included_concepts)
        child_concept = included_concepts
        # Process direct contains fields
       
        fields = {}
        print("--------------------------------")
        print("included CHILD concept #######",child_concept)
        child_concept_name = child_concept['name']
        if 'contains' in child_concept:
            for field in child_concept['contains']:
                fields[field['name']] = (field['type'], Field(description=field['description']))
        print("--------------------------------")
        print("@@@@@ fields in else #######",fields)
        dynamic_model = create_model(
                child_concept['name'], **fields
            )
        print("--------------------------------")
        print("@@@@@ dynamic model in else #######",dynamic_model)
        return {child_concept_name: dynamic_model}
        

def get_structured_output_model():
    root_concepts = yaml_data['concepts']['includes']
    for root_concept in root_concepts:
        print("--------------------------------")
        print("root concept #######",root_concept)
        leaf_concept = get_leaf_concept(root_concept)
        print("Leaf Concept: ", leaf_concept)
    return leaf_concept[root_concept['name']]
# print(root_concepts)

def extract_triplets(yaml_file):
    """
    Extract relationship triplets from YAML file.
    Only processes relationships defined in 'includes'.
    Returns list of tuples (parent, child, relation)
    """
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    
    triplets = []
    
    def process_concept(concept, parent=None):
        # Only handle includes relationships
        if 'includes' in concept:
            for included in concept['includes']:
                relation = included.get('kg_relation', 'INCLUDES')
                if parent:
                    triplets.append((parent['name'], included['name'], relation))
                # Recursively process nested includes
                process_concept(included, included)
    
    # Start processing from the root level
    if 'concepts' in data:
        process_concept(data['concepts'])

    if not triplets:
            print("No triplets found!")
    else:
        print("Relationship Triplets (Parent, Child, Relation):")
        for triplet in triplets:
            print(f"{triplet[0]} -> {triplet[2]} -> {triplet[1]}")
    return triplets


# if __name__ == "__main__":
#     print(get_structured_output_model())