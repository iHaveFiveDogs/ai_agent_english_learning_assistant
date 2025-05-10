import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from services.utiles.json_clean import *
from services.utiles.print_function_name import log_with_func_name
from ai_service.chain.chosen_text_chain import *



async def context_explainer_handle_article(user_context):
    # Invoke summarizer chain
    try:
        log_with_func_name(" 🧠  context plainer is thinking...")
        
        response = context_explainer_chain.invoke({
            "sentence": user_context
        })

        
        log_with_func_name(" 🧠  context plainer is done thinking...")
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

        
    
        response = fix_and_parse_multiple_json_objects(json_content)
        if len(response) > 1:
            print("Warning: Multiple JSON objects found. Using the first one.")
        response = response[0]
        return response
    except Exception as e:
        print(f"Failed to decode JSON: {e}")
        log_error(json_content, e)
        return None
    