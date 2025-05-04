
from agents.intelligence.word_explainer import word_explainer_handle_word_sentences
import json

async def retry_failed_words():
    with open("failed_words.json", "r", encoding="utf-8") as f:
        failed_list = json.load(f)

    chunk = {}  # Fill this if needed (for contextual use)
    word_list = [item["word"] for item in failed_list]
    await word_explainer_handle_word_sentences(chunk, word_list)

    # Remove failed words from list
    for word in word_list:
        failed_list = [item for item in failed_list if item["word"] != word]

    # Save the updated list
    with open("failed_words.json", "w", encoding="utf-8") as f:
        json.dump(failed_list, f, ensure_ascii=False, indent=4)