import google.generativeai as genai
import os
import fitz
from langchain_core.output_parsers import JsonOutputParser
from openai import OpenAI
client = OpenAI()
from typing import Optional
from langchain_openai import ChatOpenAI

PROMPT_TO_EXTRACT_CONTENT_IN_STRUCTURED_OUTPUT = """you are a helpful assistant good at extracting the contents discussed in the topic in a structured way.

"""

PROMPT_TO_PARSE_PDF = "Print the content of the input pdf file. Do not hallucinate anything. Just print the content of the pdf file."



def parse_pdf(pdf_path):
    model = genai.GenerativeModel("gemini-1.5-pro")
    sample_pdf = genai.upload_file(pdf_path)
    response = model.generate_content([PROMPT_TO_PARSE_PDF, sample_pdf])
    return response


def extract_structured_output(structured_output_model,content):
    prompt = f"""
              {PROMPT_TO_EXTRACT_CONTENT_IN_STRUCTURED_OUTPUT}
              topic: {content}
                
                """
   
    
    model = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = model.with_structured_output(structured_output_model)
    # print(structured_llm)
    response = structured_llm.invoke(prompt)
    print("Structured response: ",response)
    return response