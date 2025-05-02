
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
from utiles.json_clean import clean_content, clean_json_block, log_error,decode_json_with_retry
from utiles.llm_loader import load_llm
from prompts.chosen_text_explainer_prompt import chosen_text_explainer_prompt

try:
    chosen_text_explainer_chain = chosen_text_explainer_prompt | load_llm('chosen_text_explainer')
except Exception as e:
    print(e)








async def context_explainer_handle_article(user_context):
    # Invoke summarizer chain
    try:
        print(" 🧠  context plainer is thinking...")
        
        response = context_explainer_chain.invoke({
            "sentence": user_context
        })

        
        print(" 🧠  context plainer is done thinking...")
    # Log the raw response content for debugging
        response.content = clean_content(response.content)
        response.content = clean_json_block(response.content)
        response.content = response.content.replace('\n', '').replace('\r', '').replace('\t', '')
        response.content = response.content.replace('“', '"').replace('”', '"')  # Smart quotes to straight

        if response.content.count('"sentence"') > 1:
            print("Warning: Multiple 'sentence' keys found.")

        if response.content.count('{') != response.content.count('}'):
            print("Warning: Unbalanced braces in JSON content")
        
        # Extract JSON content between the first '{' and the last '}'
        json_start = response.content.find('{')
        json_end = response.content.rfind('}') + 1
        json_content = response.content[json_start:json_end]
        
         
        
        # Clean and validate JSON content
        json_content = json_content.replace('\n', '').replace('\t', '').replace('\r', '')
        
        # Remove trailing commas
        json_content = json_content.rstrip(', ')
        # Attempt to fix common JSON issues

        
    
        response = await decode_json_with_retry(json_content)
        
        
        
        return response
    except Exception as e:
        print(f"Failed to decode JSON: {e}")
        log_error(json_content, e)
        return None
    