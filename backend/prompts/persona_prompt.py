from langchain.prompts import ChatPromptTemplate

persona_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {persona}, reading and commenting on this article and related content."),
    ("user", "{chunk_text}")
])