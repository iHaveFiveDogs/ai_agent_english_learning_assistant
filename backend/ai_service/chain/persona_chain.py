import sys
sys.stdout.reconfigure(encoding='utf-8')


import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai_service.llm_loader.llm_ollama import load_llm
from ai_service.prompts.persona_prompt import *

try:
    persona_answer_question_chain = persona_answer_question_prompt | load_llm('persona')
    persona_selector_chain = persona_selector_prompt | load_llm('persona')
except Exception as e:
    print(e)