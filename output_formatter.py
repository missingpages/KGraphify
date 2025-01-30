from typing import get_origin,get_args,Union
import inspect
from pydantic import BaseModel
import pydantic


def getFieldDataType(field):
    origin_type = get_origin(field.annotation)
#     print(f"origin_type is {origin_type}")
    if origin_type is Union:
        annotation_args = get_args(field.annotation)
        origin_annotation = get_origin(annotation_args[0])
#         print(f"origin_annotation is {origin_annotation}")
        if origin_annotation is list:
            actual_field = get_args(annotation_args[0])[0]
            print(actual_field)
#             print(f"is it class? {inspect.isclass(actual_field)}")
#             print(f"is it pydantic class? {isinstance(actual_field,pydantic._internal._model_construction.ModelMetaclass)}")
            if isinstance(actual_field,pydantic._internal._model_construction.ModelMetaclass):
                return actual_field
            else:
                return None
        elif isinstance(origin_annotation,pydantic._internal._model_construction.ModelMetaclass):
#             print(f"its a Pydantic class:{origin_annotation}")
            return origin_annotation
    elif origin_type is None:
#         print(field.annotation)
        if field.annotation is str or field.annotation is int or field.annotation is float:
            return field.annotation
        else:
            field_type = type(field.annotation)
#             print(f"field type is {field_type}")
            if isinstance(field.annotation,pydantic._internal._model_construction.ModelMetaclass):
#                 print(f"Pydantic class:{field.annotation}")
                return field.annotation
        
    else:
        return None


def getFieldTypeForClass(pydanticClass,attr):
    fields = pydanticClass.model_fields
#     print(fields)
    field = fields[attr]
    data_type = getFieldDataType(field)
    return data_type


def parsedict(root_class,content,node_props):
    node_name = root_class.__name__
    for k,v in content.items():
        print(f" processing key ---{k}")
        data_type = getFieldTypeForClass(root_class,k)
        isChildNode = isinstance(data_type,pydantic._internal._model_construction.ModelMetaclass)
        if not isChildNode:
            print("NOT CHILD NODE")
            node_props[node_name][k]=v
            print(node_props)
        else:

            if not 'includes' in node_props[node_name]:
                print("no includes so creating a key",node_props[node_name])
                node_props[node_name]['includes']=[]
            props_for_child = build_schema_dict(data_type,v,node_props[node_name])
            print("-------------------------")
            print("props of child",props_for_child)
            node_props[node_name]['includes'].append(props_for_child)
    return node_props
    



def build_schema_dict(root_class,content,node_props):
    node_name = root_class.__name__
    print("________________________________")
    print(f"content processe for {node_name} is {content}")
    print(f"node props is {node_props}")
    
    if type(content) is dict:
        node_props = {node_name:{}}
        node_props = parsedict(root_class,content,node_props)    
        
    elif type(content) is list:
        node_props_list = []
        for item in content:
#             print(item)
            node_props = {node_name:{}}
            node_props = parsedict(root_class,item,node_props) 
            
            node_props_list.append(node_props[node_name])
            print("***************************")
            print(f"node_props_list is {node_props_list}")
        node_props = {node_name:node_props_list}
    print(f"returned node props {node_props}")         
    return node_props 