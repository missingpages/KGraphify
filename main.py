import google.generativeai as genai
import os
import fitz
from langchain_core.output_parsers import JsonOutputParser
from openai import OpenAI
client = OpenAI()
from typing import Optional
from schema_reader import load_schema,read_entities,read_relations
from class_generator import create_structured_output_model
from llm import extract_structured_output
from langchain_community.document_loaders import PyPDFLoader
import sys
import json
import argparse
from kg_builder import *

def read_content_from_pdf(pdf_file_path):
#     pdf_file_path = "data/leph101.pdf"
    loader = PyPDFLoader(pdf_file_path)
    docs = loader.load()
    print(len(docs))
    content = ''
    for doc in docs:
        content += doc.page_content[0:]
    return content

def main(yaml_file=None, pdf_file=None):
    print("\n📚 Starting Knowledge graph building Pipeline")
    print(f"Input schema file (yaml): {yaml_file}")
    entities,relations = None,None
    # Step 1: Extract get structured output model from the yaml file
    print("\n📑 Step 1/6: read schema from yaml file")
    if yaml_file is None:
        print("No yaml file provided, using default schema")
    else:
        schema = load_schema(yaml_file)
        entities,relations = read_entities(schema),read_relations(schema)


    print("\n📑 Step 2/6: Read content from pdf file")
    content = read_content_from_pdf(pdf_file)
    
    
    # Step 3: Extract structured output from the content
    print("\n📑 Step 3/6: create structured output model from schema")
    structured_output_model = create_structured_output_model(entities,relations)

    # Step 4: Extract structured output from the content
    print("\n📑 Step 4/6: Extract structured output from the content")
    structured_output = extract_structured_output(structured_output_model, content)
    structured_output = json.loads(structured_output.model_dump_json())
    print(structured_output)

    # Step 5: Build graph nodes for entities
    print("\n📑 Step 5/6: Build graph nodes for entities")   
    entity_nodes = structured_output['entities'] 
    create_nodes(entity_nodes)

    # Step 6: Build graph nodes for relations
    print("\n📑 Step 6/6: Build graph nodes for relations")     
    rel_nodes = structured_output['relations']
    create_relations(rel_nodes) 



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Build knowledge graph from PDF using schema')
    parser.add_argument('--yaml', type=str, help='Path to YAML schema file')
    parser.add_argument('--pdf', type=str, required=True, help='Path to PDF file')
    args = parser.parse_args()
    yaml_file = args.yaml
    pdf_file = args.pdf
    main(yaml_file, pdf_file)
