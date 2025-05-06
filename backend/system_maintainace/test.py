#### to make project file available####
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')
#### to make project file available####



# test 1  /upload_article ok

# import requests

# url = "http://localhost:8000/upload_article/"
# payload = {
#     "title": "Sample Article",
#     "source": "Test Source",
#     "content": "This is a test article content."
# }

# response = requests.post(url, json=payload)
# print(response.json())

####################################################################################################################################################
# test LLM connection ok

# from langchain.prompts import ChatPromptTemplate
# from langchain_community.chat_models import ChatOllama  # or ChatOpenAI

# llm = ChatOllama(model="gemma3:latest")

# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a helpful assistant."),
#     ("user", "{input}")
# ])

# chain = prompt | llm

# response = chain.invoke({"input": "What is the capital of France?"})
# print(response.content)

####################################################################################################################################################
# test 3  chunking_article ok
# from services.chunk_article_service import chunk_article

# async def test_chunk_article():
#     # Example article content
#     article_id = "test_article_4"
#     content = """
#     When Deepankar Rustagi last raised money for OmniRetail in 2022, excitement was high for African startups addressing the supply chain and operational challenges in the fast-moving consumer goods (FMCG) sector. At one point, these startups received more capital than all sectors, except fintech.

# Recently, though, the industry’s enthusiasm and venture capital’s interest have faded, as various business models have struggled under mounting pressure.

# Yet for Rustagi, OmniRetail isn’t just another B2B commerce platform; it’s an ambitious effort to reshape informal retail across Nigeria and West Africa using technology and embedded finance in a scalable, profitable way. Now, that vision has received further endorsement with a $20 million Series A equity funding round. This capital will help OmniRetail expand its presence in Nigeria, Ghana, and Ivory Coast, while deepening its focus on embedded finance products.

# The round was co-led by Norwegian development finance institution Norfund and Lagos-based VC firm Timon Capital, with follow-on participation from Ventures Platform, Aruwa Capital, Goodwell Investments (via Alitheia Capital), and Flour Mills of Nigeria.

# This marks Norfund’s first direct equity investment in an African startup, and according to Rustagi, puts OmniRetail on a path to dominating in a segment where others have struggled to grow profitably. OmniRetail has raised $38 million in equity and debt since its inception in 2019. 

# OmniRetail’s model digitizes order management for 145 manufacturers, more than 5,800 distributors and services over 150,000 informal retailers across 12 cities in Nigeria, Ghana and Ivory Coast.

# Retailers use the app to order inventory, access working capital, and make digital payments. In the background is a third-party logistics network of over 1,100 vehicles and distributed warehousing capacity managed by 85 local logistics partners. 
#     """
    
#     # Call the chunk_article function
#     await chunk_article(article_id, content)
    
#     # Fetch chunks from the database to verify
#     from db.mongodb import articles_chunks
#     chunks = await articles_chunks.find({"article_id": article_id}).to_list(length=None)
    
#     # Print chunks for verification
#     for chunk in chunks:
#         print(f"Chunk {chunk['chunk_index']}: {chunk['chunk_text']}")
    
#     # Add assertions if needed
#     assert len(chunks) > 0, "No chunks were created"
#     print("Test passed!")

# import asyncio

# if __name__ == "__main__":
#     asyncio.run(test_chunk_article())

# ##################### json format test ##############################
# # import json

# # raw = '{"summary": "Deepankar Rustagi founded OmniRetail in 2022, initially attracting more investment than other sectors, including fintech. Recently, however, industry enthusiasm has diminished due to business model challenges. However, OmniRetail is now receiving $20 million in Series A funding from Norfund, Lagos-based VC firm Timon Capital, and several other investors. This funding will support expansion into Nigeria, Ghana, and Ivory Coast, and deepen its focus on embedded finance. This strategic investment positions OmniRetail to become a dominant force in the African informal retail market, leveraging technology and financial solutions."}'

# # parsed = json.loads(raw)
# # print(parsed)


# #############test upload article######################################################################################################################################
# from services.chunk_article_service import upload_article_to_db,clean_content
# import asyncio
# from db.mongodb import articles_raw
# from datetime import datetime
# from services.chunk_article_service import clean_content
# from ai_service.intelligence.chosen_text_explainer import context_explainer_handle_article
# from services.chunk_article_service import chunk_article, upload_article_to_db
# from ai_service.intelligence.alfo import alfo_handle_chunked_article_decision

# clean_content = clean_content(""" 

# Elon Musk’s SpaceX is getting its own official company town.

# Residents of an area around SpaceX’s Starbase launch site in southern Texas voted overwhelmingly on Saturday to incorporate as a city — also named Starbase. According to results posted online by the Cameron County Elections Department, there were 212 votes in favor and only six against.

# In a post on his social media site X, Musk wrote that Starbase, Texas “Is now a real city!” 

# The new city’s residents are believed to mostly be SpaceX employees. On Saturday, they also voted to elect three current and former SpaceX employees — Bobby Peden, Jordan Buss, and Jenna Petrzelka — who ran unopposed to serve, respectively, as Starbase’s mayor and two commissioners.

# The Associated Press reports that SpaceX hasn’t shared many specifics about why it wanted to incorporate the area. The company said it already manages the roads, utilities, and “the provisions of schooling and medical care,” and it’s also looking to shift authority from the county to the new city government to close the nearby Boca Chica beach and state park for launches.

# Musk — who recently said he would be reducing his role with the Trump administration’s controversial Department of Government Efficiency to a “day or two” per week — announced last year that he was moving SpaceX’s headquarters from El Segundo, California to the Starbase facility in Texas. 

# At the time, Musk said he’d “had enough of dodging gangs of violent drug addicts just to get in and out of the building” and that the “final straw” was a California bill that prohibits schools from disclosing students’ sexuality or gender identity without consent.

# Exhibit at TechCrunch Sessions: AI
# Secure your spot at TC Sessions: AI and show 1,200+ decision-makers what you’ve built — without the big spend. Available through May 9 or while tables last.
# Berkeley, CA | June 5
# BOOK NOW
# After last night’s election, a new X account representing the town posted, “Becoming a city will help us continue building the best community possible for the men and women building the future of humanity’s place in space.”n


# """)



# article = {
#     "title": "Residents of SpaceX’s Starbase launch site vote to incorporate as a city",
#     "source": "bbc.com",
#     "upload_date": datetime.utcnow(),
#     "content": clean_content
# }

# if __name__ == "__main__":
#     import asyncio

#     async def main():
#         print("test time:" , datetime.utcnow())
#         article_id = await upload_article_to_db(article)
#         await chunk_article(article_id)
#         await alfo_handle_chunked_article_decision(article_id)

#     asyncio.run(main())


########### precache words######################################################################################################################################

# from agents.intelligence.word_explainer import precache_ipa_etymology_from_txt
# import asyncio
# import os

# base_dir = os.path.dirname(__file__)
# txt_path = os.path.join(base_dir, "..", "resources", "gre_vertical_wordlist.txt")  #intermediate_chunk_6,advanced_chunk_5

# if __name__ == "__main__":
#     asyncio.run(precache_ipa_etymology_from_txt(txt_path))



########### precache words######################################################################################################################################


##############################test vector persona####################################################
# import sys
# import os
# sys.stdout.reconfigure(encoding='utf-8')
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from services.utiles.json_clean import *
# from services.persona_service import *
# from agents.chain.persona_chain import *
# from agents.memory.persona_vector import *
# from agents.tool.persona_tool import *
# from agents.memory.persona_vector import get_retriver
# import asyncio

# async def test(input, query):
#     retriever = await get_retriver(input)

#     docs = retriever.get_relevant_documents(query)

#     context = "\r\n".join([doc.page_content for doc in docs])
#     print("🧠  Persona is thinking")
#     response = await persona_chain.ainvoke({
#         "persona": "investor",
#         "context": context,
#         "question": query
#     })
#     print("🧠  Persona is done thinking")
#     if response.content:
#         print("Response:", response.content)
#     else:
#         print("No response received.")
    

# if __name__ == "__main__":
#     input = asyncio.run(gather_single_persona_docs("investor"))
#     asyncio.run(test(input, "What would the investor say about the technology trend?"))

# test langchain agent

# import asyncio

# from ai_service.llm_loader.llm_ollama import load_llm
# from ai_service.agents.talk_organizer import initialize_persona_agent


# async def test_agent_executor():
#     # Load the raw LLM (not a chain!)
#     llm = load_llm("persona")

#     # Initialize agent
#     agent_executor = await initialize_persona_agent(llm)

#     # Query the agent
#     user_question = """ what's this mean? Developing and selling video game cheats can be a lucrative business, and video game developers have in recent years had to beef up their anti-cheat teams, whose mission is to ban cheaters, neutralize the software they use, as well as go after cheat developers. """
#     result = await agent_executor.ainvoke({"input": {"query": user_question}})
    
#     # Output the response
#     print("💬 Agent's Final Response:\n", result)

# # Run the test
# if __name__ == "__main__":
#     asyncio.run(test_agent_executor())


# import redis

# r = redis.Redis(host='localhost', port=6379, decode_responses=True)
# print(r.ping()) 

from fastapi.testclient import TestClient
from routes.get_upload_progress import router
 # Set progress to 42
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

def test_get_progress():
    client = TestClient(app)
    job_id = "0db45d34-97bd-46d6-9a84-6dde403e995e"
    response = client.get(f"/progress/{job_id}")
    assert response.status_code == 200
    # You can check for the expected progress value if you know it
    print(response.json())

import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.set("0db45d34-97bd-46d6-9a84-6dde403e995e", 42) 
if __name__ == "__main__":
    test_get_progress()