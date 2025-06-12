import sys
sys.stdout.reconfigure(encoding='utf-8')


import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai_service.prompts.generate_question_prompt import question_generator_prompt, question_feedback_prompt
from ai_service.llm_loader.llm_ollama import load_llm

try:
    generate_question_chain = question_generator_prompt | load_llm('generate_question')
    generate_question_chain2 = question_generator_prompt | load_llm('generate_question2')
    question_feedback_chain = question_feedback_prompt | load_llm('generate_question')
except Exception as e:
    print(e)