import sys
sys.stdout.reconfigure(encoding='utf-8')


import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai_service.prompts.context_explainer_prompt import chosen_text_explainer_prompt
from ai_service.llm_loader.llm_ollama import load_llm

try:
    context_explainer_chain = chosen_text_explainer_prompt | load_llm('context_explainer')
except Exception as e:
    print(e)