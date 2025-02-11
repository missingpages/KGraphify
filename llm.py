import google.generativeai as genai
import os
import fitz
from langchain_core.output_parsers import JsonOutputParser
from openai import OpenAI
client = OpenAI()
from typing import Optional
from langchain_openai import ChatOpenAI

PROMPT_TO_EXTRACT_CONTENT = """you are a helpful assistant good at extracting the contents discussed in the topic in a structured way.

"""



def get_llm():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return llm


def extract_structured_output(structured_output_model,content):
    prompt = f"""
              {PROMPT_TO_EXTRACT_CONTENT}
              
              
              topic: Chapter 1- Basic physics concepts
1.4 BASIC PROPERTIES OF ELECTRIC CHARGE
We have seen that there are two types of charges, namely positive and negative and their effects tend to cancel each other. Here, we shall now describe some other properties of the electric charge.
If the sizes of charged bodies are very small as compared to the distances between them, we treat them as point charges. All the charge content of the body is assumed to be concentrated at one point in space.
1.4.1 Additivity of charges
We have not as yet given a quantitative definition of a charge; we shall follow it up in the next section. We shall tentatively assume that this can be done and proceed. If a system contains two point charges q1 and q2, the total charge of the system is obtained simply by adding
4
algebraically q1 and q2 , i.e., charges add up like real numbers or they are scalars like the mass of a body. If a system contains n charges q1, q2,q3,...,qn,thenthetotalchargeofthesystemisq1 +q2 +q3 +...+qn . Charge has magnitude but no direction, similar to mass. However, there is one difference between mass and charge. Mass of a body is always positive whereas a charge can be either positive or negative. Proper signs have to be used while adding the charges in a system. For example, the total charge of a system containing five charges +1, +2, –3, +4 and –5, in some arbitrary unit, is (+1) + (+2) + (–3) + (+4) + (–5) = –1 in the same unit.
1.4.2 Charge is conserved
We have already hinted to the fact that when bodies are charged by rubbing, there is transfer of electrons from one body to the other; no new charges are either created or destroyed. A picture of particles of electric charge enables us to understand the idea of conservation of charge. When we rub two bodies, what one body gains in charge the other body loses. Within an isolated system consisting of many charged bodies, due to interactions among the bodies, charges may get redistributed but it is found that the total charge of the isolated system is always conserved. Conservation of charge has been established experimentally.

              """
   
    
    model = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = model.with_structured_output(structured_output_model)
    print(structured_llm)
    response = structured_llm.invoke(prompt)
    print(response)
    return response