import sys
sys.stdout.reconfigure(encoding='utf-8')


import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_service.prompts.alfo_prompt import *
from ai_service.llm_loader.llm_ollama import load_llm



try:
    alfo_handle_chunked_article_chain = alfo_handle_chunked_article_prompt | load_llm('alfo')
except Exception as e:
    print(e)
 