from langchain.prompts import ChatPromptTemplate

persona_answer_question_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an expert assistant that answers user questions based on memory.\n"
     "If a persona is given, respond as that persona using the memory.\n"
     
     "Context Memory:\n{context}\n\n"
     "Persona: {persona}\n"
     "Question: {question}\n\n"
     "- Respond in pure JSON, like this:\n"
     '{{\"answer\": \"...\"}}\n'
     "- Do not include backticks, Markdown, or explanations.\n")
])

persona_selector_prompt = ChatPromptTemplate.from_template("""
   You are selecting a persona for the following user query:
  "{query}"

Choose the best matching persona from this list:
{persona_list}



"- Respond in **pure JSON**, without any Markdown formatting or extra text.\n"
     "- Do **not** include \`json or backticks.\n"
     "- Only output JSON like this:\n"
     "{{\"persona\": \"...\"}}."

     If the persona is not provided or not available, invent one based on the {query}.

""")