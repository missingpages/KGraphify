import google.generativeai as genai
import os
import fitz
from langchain_core.output_parsers import JsonOutputParser
from openai import OpenAI
client = OpenAI()
from typing import Optional
from langchain_openai import ChatOpenAI
from graph_schema_reader import get_structured_output_model, extract_triplets

PROMPT_TO_EXTRACT_CONTENT = """you are a helpful assistant good at extracting the contents discussed in the topic in a structured way.

"""

def get_llm():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return llm


def extract_structured_output(content):
    prompt = f"""
              {PROMPT_TO_EXTRACT_CONTENT}
              
              
              topic: {content}
              """
    model = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_output_model = get_structured_output_model()
    structured_llm = model.with_structured_output(structured_output_model)
    response = structured_llm.invoke(prompt)
    return response