import sys
sys.stdout.reconfigure(encoding='utf-8')


import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from ai_service.prompts.summarizer_prompt import summarizer_prompt
from ai_service.llm_loader.llm_ollama import load_llm

try:
    summarizer_chain = summarizer_prompt | load_llm('summarizer')
except Exception as e:
    print(e)