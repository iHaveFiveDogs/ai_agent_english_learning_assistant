
import sys
sys.stdout.reconfigure(encoding='utf-8')


import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai_service.prompts.sentence_explainer_prompt import *
from ai_service.llm_loader.llm_ollama import load_llm

try:
    sentence_explainer_chain = key_sentence_explainer_prompt | load_llm('sentence_explainer')
except Exception as e:
    print(e)
