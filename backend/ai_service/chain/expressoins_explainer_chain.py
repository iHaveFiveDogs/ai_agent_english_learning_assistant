

sys.stdout.reconfigure(encoding='utf-8')


import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai_service.prompts.expressions_explainer_prompt import *
from ai_service.llm_loader.llm_ollama import load_llm

try:
    
    expressions_explainer_chain = expressions_explainer_prompt | load_llm('expressions_explainer')
    contextual_expression_explainer_chain = contextual_expression_explainer_prompt | load_llm('expressions_explainer')
except Exception as e:
    print(e)

