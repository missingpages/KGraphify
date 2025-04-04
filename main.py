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

from llama_index import Document
from llama_index.node_parser import TokenTextSplitter

def chunk_pdf_by_tokens(pdf_path: str, chunk_size: int = 512, chunk_overlap: int = 50) -> list:
    """
    Chunks a PDF file by tokens with specified overlap using LlamaIndex's TokenTextSplitter
    
    Args:
        pdf_path (str): Path to the PDF file
        chunk_size (int): Number of tokens per chunk
        chunk_overlap (int): Number of overlapping tokens between chunks
        
    Returns:
        list: List of text chunks
    """
    # Get PDF content using existing function
    content = read_content_from_pdf(pdf_path)
    # Initialize the token text splitter
    text_splitter = TokenTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    # Split into chunks
    chunks = text_splitter.split_text(content)
    return chunks


def pdf_content_generator(pdf_path: str, return_as: str = 'full', chunk_size: Optional[int] = 512, chunk_overlap: Optional[int] = 50):
    """
    Generator function that yields PDF content based on specified return type
    
    Args:
        pdf_path (str): Path to the PDF file
        return_as (str): How to return content - 'page', 'full' or 'chunk'
        chunk_size (int, optional): Number of tokens per chunk if return_as='chunk'
        chunk_overlap (int, optional): Number of overlapping tokens between chunks if return_as='chunk'
        
    Yields:
        str: PDF content according to specified return type
    """
    if return_as not in ['page', 'full', 'chunk']:
        raise ValueError("return_as must be one of: 'page', 'full', 'chunk'")
        
    if return_as == 'full':
        yield read_content_from_pdf(pdf_path)
        
    elif return_as == 'page':
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        for doc in docs:
            yield doc.page_content
            
    elif return_as == 'chunk':
        if chunk_size is None or chunk_overlap is None:
            raise ValueError("chunk_size and chunk_overlap must be specified when return_as='chunk'")
            
        chunks = chunk_pdf_by_tokens(pdf_path, chunk_size, chunk_overlap)
        for chunk in chunks:
            yield chunk



def read_content_from_pdf(pdf_file_path):
    """Generator function that yields content from PDF file page by page"""
    loader = PyPDFLoader(pdf_file_path)
    docs = loader.load()
    for doc in docs:
        yield doc.page_content
    

def main(yaml_file=None, pdf_dir=None, process_as=None, chunk_size=None, chunk_overlap=None):
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
    
    # Step 2: create structured output model from schema
    print("\n📑 Step 2/6: create structured output model from schema")
    structured_output_model = create_structured_output_model(entities,relations)

    print("\n📑 Step 3/6: Read content from pdf directory")
    if pdf_dir is None:
        raise ValueError("PDF directory must be specified")
        
    # Get list of PDF files in directory
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    if not pdf_files:
        raise ValueError(f"No PDF files found in directory: {pdf_dir}")
        
    print(f"Found {len(pdf_files)} PDF files")
    
    # Process each PDF file
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        print(f"\nProcessing PDF file: {pdf_file}")

        # For 'full' process, collect all content first
        if process_as == 'full':
            if gemini_pdf_parsing:
                content = parse_pdf(pdf_path)
            else:
                content = []
                for page_content in read_content_from_pdf(pdf_path):
                    content.append(page_content)
                content = ' '.join(content)
            
            # Process full content at once
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
            
        # For other modes, process each chunk separately
        else:
            if process_as == 'chunk':
                content_generator = pdf_content_generator(pdf_path, process_as, chunk_size, chunk_overlap)
            elif process_as == 'page':
                content_generator = pdf_content_generator(pdf_path, process_as)
            elif process_as == 'context':
                content_generator = read_content_from_pdf(pdf_path)
                
            # Process each chunk
            for i,chunk in enumerate(content_generator):
                print(f"\n📑 Step {i+4}/6: Extract structured output from chunk {i+1} of {len(content_generator)}")
                structured_output = extract_structured_output(structured_output_model, chunk)
                structured_output = json.loads(structured_output.model_dump_json())
                print(structured_output)

                # Step 5: Build graph nodes for entities
                print(f"\n📑 Step {i+5}/6: Build graph nodes for entities")   
                entity_nodes = structured_output['entities'] 
                create_nodes(entity_nodes)

                # Step 6: Build graph nodes for relations
                print(f"\n📑 Step {i+6}/6: Build graph nodes for relations")     
                rel_nodes = structured_output['relations']
                create_relations(rel_nodes)

        



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Build knowledge graph from PDF using schema')
    parser.add_argument('--yaml', type=str, help='Path to YAML schema file')
    parser.add_argument('--pdf_dir', type=str, required=True, help='Directory containing PDF files')
    parser.add_argument('--process_as', type=str, choices=['page', 'full', 'context','chunk'], required=True, help='chunking strategy (page, full, or context)')
    parser.add_argument('--chunk_size', type=int, help='Size of chunks when process_as=chunk')
    parser.add_argument('--chunk_overlap', type=int, help='Overlap between chunks when process_as=chunk')
    parser.add_argument('--gemini_pdf_parsing', type=bool, default=False, help='Whether to use Gemini for PDF parsing')
    args = parser.parse_args()
    yaml_file = args.yaml
    pdf_dir = args.pdf_dir
    process_as = args.process_as
    chunk_size = args.chunk_size if process_as == 'chunk' else None
    chunk_overlap = args.chunk_overlap if process_as == 'chunk' else None
    gemini_pdf_parsing = args.gemini_pdf_parsing if process_as == 'full' else False
    main(yaml_file, pdf_dir, process_as, chunk_size, chunk_overlap, gemini_pdf_parsing)
