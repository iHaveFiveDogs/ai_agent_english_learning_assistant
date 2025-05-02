
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
from utiles.json_clean import clean_content, clean_json_block, log_error
from utiles.llm_loader import load_llm
from prompts.persona_prompt import persona_prompt

try:
    persona_chain = persona_prompt | load_llm('persona')
except Exception as e:
    print(e)