import re
import json
from datetime import datetime
import asyncio
import unicodedata
def clean_content(text):
    # Remove invisible characters
    text = re.sub(r'[\u200b-\u200f\u2028\u2029]', '', text)

    # Normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # Replace smart quotes
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")

    # Remove any strange tabs or carriage returns
    text = text.replace('\t', ' ').replace('\r', '')

    # Optional: remove weird unicode (like emoji) if you want
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = text.encode('utf-8', 'ignore').decode('utf-8')
    
    return text
def clean_json_block(raw_response):
    if raw_response.startswith('```json'):
        raw_response = raw_response.strip('`')  # Remove all backticks
        raw_response = raw_response.replace('json\n', '', 1)  # Remove 'json' after ```
    return raw_response.strip()

def log_error(content, error):
    with open("e:/python_project/article_ai_agent_v_1/backend/error_log.txt", "a") as log_file:
        log_file.write(f"Time: {datetime.now()}\n")
        log_file.write(f"Content: {content}\n")
        log_file.write(f"Error: {error}\n\n")

def clean_ipa(ipa):
    # Simple regex to filter valid IPA symbols (broad coverage)
    pattern = re.compile(r"[/\[\]a-zA-Z\u0250-\u02AF\u0300-\u036F\s.]+")
    match = pattern.search(ipa)
    return match.group(0).strip() if match else ipa

async def decode_json_with_retry(json_content, retries=3):
    for attempt in range(retries):
        try:
            cleaned_content = clean_json_block(json_content)
            return json.loads(cleaned_content)
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(1)
            else:
                print("Max retries reached. Skipping this item.")
                log_error(json_content, e)
                return None

async def retry_failed_words():
    with open("failed_words.json", "r", encoding="utf-8") as f:
        failed_list = json.load(f)

    chunk = {}  # Fill this if needed (for contextual use)
    word_list = [item["word"] for item in failed_list]
    await word_explainer_handle_word_sentences(chunk, word_list)

def extract_json_from_response(content):
    try:
        first_brace = content.index('{')
        last_brace = content.rindex('}') + 1
        return content[first_brace:last_brace].replace('\n', '').replace('\t', '').replace('\r', '')
    except ValueError:
        return None

def find_weird_unicode_chars(text):
    weird_chars = []
    for ch in text:
        code = ord(ch)
        if code > 127:  # ASCII-safe range
            char_info = {
                "char": ch,
                "unicode": f"U+{code:04X}",
                "name": unicodedata.name(ch, "UNKNOWN")
            }
            weird_chars.append(char_info)
    return weird_chars