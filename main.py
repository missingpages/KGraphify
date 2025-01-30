import google.generativeai as genai
import os
import fitz
from langchain_core.output_parsers import JsonOutputParser
from openai import OpenAI
client = OpenAI()
from typing import Optional
from graph_schema_reader import get_structured_output_model, extract_triplets
from llm import extract_concept_graph
from langchain_community.document_loaders import PyPDFLoader

def read_content_from_pdf(pdf_file_path):
#     pdf_file_path = "../leph101.pdf"
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    print(len(docs))
    content = ''
    for doc in docs:
        content += doc.page_content[0:]
    return content

def main(yaml_file, pdf_file):
    print("\n📚 Starting Knowledge graph building Pipeline")
    print(f"Input schema file (yaml): {yaml_file}")

    # Step 1: Extract get structured output model from the yaml file
    print("\n📑 Step 1/4: get structured output model from the yaml file")
    structured_output_model = get_structured_output_model(yaml_file)

    # Step 2: Read content from pdf file
    print("\n📑 Step 2/4: Read content from pdf file")
    content = read_content_from_pdf(pdf_file)
    
    
    # Step 3: Extract structured output from the content
    print("\n📑 Step 3/4: Extract structured output from the content")
    structured_output = extract_structured_output(structured_output_model, content)
    structured_output = json.loads(structured_output.model_dump_json())
    print(structured_output)

    # Step 4: Build schema dict
    print("\n📑 Step 4/4: Build schema dict")   
    structured_output_matching_schema = build_schema_dict(structured_output_model,structured_output,{})
    print(structured_output_matching_schema)

    # Step 5: Build KG
    print("\n📑 Step 5/5: Build KG")
    root_key = list(structured_output_matching_schema.keys())[0]  
    root_values = structured_output_matching_schema[root_key]  
    buildKG(root_key,root_values)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <yaml_file> <pdf_file>")
        sys.exit(1)
    yaml_file = sys.argv[1]
    pdf_file = sys.argv[2]
    main(yaml_file, pdf_file)
