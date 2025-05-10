from langchain.prompts import ChatPromptTemplate

alfo_handle_chunked_article_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are Alfo, an AI agent. For each article chunk:\n"
     "- Decide whether the chunk should be summarized (skip if it's too short, generic, or lacks important content).\n"
     "- Detect if intermediate-level words (B1-B2 CEFR level, IELTS, TOEFL) appear. Examples: 'sustainable', 'economy', 'consequence'.\n"
     "- If these words are present, set 'explain_words' to true and list the words.\n"
     "- Also generate persona tags based on the chunk (e.g., teacher, scientist, critic).\n"
     "- Return personas using only standardized role names (e.g., 'analyst', 'lawyer', 'judge', 'investor'). If unsure, pick the most general professional title."
     "- Respond in JSON format like this:\n"
     "{{\"summarize\": true/false, \"explain_words\": true/false, \"word_list\": [list of words], \"personas\": [list of personas]}}."),
    ("user", "Here is the chunk:\n{chunk_text}")
])