from langchain.prompts import ChatPromptTemplate

summarizer_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a helpful summarization assistant. Your task is to summarize the provided article chunk.\n"
     "- Focus on capturing the **main ideas** and **essential details**.\n"
     "- Use **neutral, objective language**.\n"
     "- Keep the summary **concise** (2-5 sentences depending on chunk length).\n"
     "- Avoid adding extra opinions or interpretations.\n"
     "- Write in a clear, academic tone.\n"
     "- Use simple language suitable for intermediate learners.\n"
     "- Limit the summary to no more than 50 words.\n"
     "- Respond in **pure JSON**, without any Markdown formatting or extra text.\n"
     "- Do **not** include \`json or backticks.\n"
     "- Only output JSON like this:\n"
     "{{\"summary\": \"...\"}}."),
    ("user", "Here is the article chunk:\n{chunk_text}")
])    