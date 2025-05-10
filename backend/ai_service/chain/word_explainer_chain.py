
import sys
sys.stdout.reconfigure(encoding='utf-8')


import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai_service.prompts.word_explainer_prompt import *
from ai_service.llm_loader.llm_ollama import load_llm

try:
    
    word_cached_chain = word_cached_prompt | load_llm('word_explainer')
    batch_ipa_chain = batch_ipa_prompt | load_llm('word_explainer')
    contextual_explainer_chain = contextual_explainer_prompt | load_llm('word_explainer')
except Exception as e:
    print(e)

