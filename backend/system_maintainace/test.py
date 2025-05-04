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

##################### json format test ##############################
# import json

# raw = '{"summary": "Deepankar Rustagi founded OmniRetail in 2022, initially attracting more investment than other sectors, including fintech. Recently, however, industry enthusiasm has diminished due to business model challenges. However, OmniRetail is now receiving $20 million in Series A funding from Norfund, Lagos-based VC firm Timon Capital, and several other investors. This funding will support expansion into Nigeria, Ghana, and Ivory Coast, and deepen its focus on embedded finance. This strategic investment positions OmniRetail to become a dominant force in the African informal retail market, leveraging technology and financial solutions."}'

# parsed = json.loads(raw)
# print(parsed)


#############test upload article######################################################################################################################################
# from services.chunk_article_service import upload_article_to_db,clean_content
# import asyncio
# from db.mongodb import articles_raw
# from datetime import datetime
# from services.chunk_article_service import clean_content
# from agents.intelligence.chosen_text_explainer import context_explainer_handle_article
# from services.chunk_article_service import chunk_article, upload_article_to_db
# from agents.intelligence.alfo import alfo_handle_chunked_article_decision

# clean_content = clean_content(""" 

# The Duke of Sussex has told the BBC he "would love a reconciliation" with the Royal Family, in an emotional interview in which he said he was "devastated" at losing a legal challenge over his security in the UK.

# Prince Harry said the King "won't speak to me because of this security stuff", but that he did not want to fight any more and did "not know how much longer my father has".

# The prince spoke to BBC News in California after losing an appeal over the levels of security he and his family are entitled to while in the UK.

# Buckingham Palace said: "All of these issues have been examined repeatedly and meticulously by the courts, with the same conclusion reached on each occasion."


# Watch: Prince Harry's exclusive interview in full
# After Friday's court ruling, the prince said: "I can't see a world in which I would bring my wife and children back to the UK at this point."

# "There have been so many disagreements between myself and some of my family," he added, but had now "forgiven" them.

# "I would love reconciliation with my family. There's no point continuing to fight any more, life is precious," said Prince Harry, who said the dispute over his security had "always been the sticking point".

# Prince Harry loses legal challenge over security
# Six key moments from Prince Harry's BBC interview

# The prince had wanted to overturn changes to his security that were introduced in 2020 as he stepped down as a working royal and moved to the United States.

# Saying that he felt "let down", he described his court defeat as a "good old fashioned establishment stitch up" and blamed the Royal Household for influencing the decision to reduce his security.

# Asked whether he had asked the King to intervene in the dispute over security, Prince Harry said: "I never asked him to intervene - I asked him to step out of the way and let the experts do their jobs."

# The prince said his treatment during the process of deciding his security had "uncovered my worst fears".

# He said of the decision: "I'm devastated - not so much as devastated with the loss that I am about the people behind the decision, feeling as though this is okay. Is it a win for them?"

# He continued: "I'm sure there are some people out there, probably most likely the people that wish me harm, [who] consider this a huge win."

# Prince Harry said the decision to remove his automatic security entitlement impacts him "every single day", and has left him in a position where he can only safely return to the UK if invited by the Royal Family - as he would get sufficient security in those circumstances.

# Getty Images The Duke and Duchess of Sussex walk out of a door. The duchess is waving and smiling. Prince Harry is wearing a white shirt and a black blazer and trousers. Meghan is wearing a white shirt and a beige blazer and trousers. Prince Harry has ginger hair, a ginger beard, and blue eyes. Meghan has long brown hair and brown eyes.Getty Images
# The Duke and Duchess of Sussex, pictured in April, have been living in the US since 2020

# The prince said changes to his security status in 2020 had impacted not just him, but his wife and, later, his children too.

# He went on to say: "Everybody knew that they were putting us at risk in 2020 and they hoped that me knowing that risk would force us to come back.

# "But then when you realise that didn't work, do you not want to keep us safe?

# "Whether you're the government, the Royal Household, whether you're my dad, my family - despite all of our differences, do you not want to just ensure our safety?"

# Asked whether he missed the UK, he added: "I love my country, I always have done, despite what some people in that country have done... and I think that it's really quite sad that I won't be able to show my children my homeland."

# Prince Harry said he would not be seeking a further legal challenge, saying Friday's ruling had "proven that there was no way to win this through the courts".

# "I wish someone had told me that beforehand," he said, adding that the ruling had been a "surprise".

# He continued: "This, at the heart of it, is a family dispute, and it makes me really, really sad that we're sitting here today, five years later, where a decision that was made most likely, in fact I know, to keep us under the roof."

# Harry's emotional avalanche hits the Royal Family

# Prince Harry spoke to the BBC shortly after losing his latest legal challenge against the UK government over the level of security he and his family are entitled to when visiting.

# The Court of Appeal dismissed the prince's case, which hinged on how an official committee made the decision to remove his eligibility for automatic, full-scale protection in line with what other senior royals receive.

# On Friday, the court ruled that Prince Harry had made "powerful" arguments about the level of threat he and his family face, but said his "sense of grievance" did not "translate into a legal argument".

# His legal complaint centred around a committee called the Protection of Royalty and Public Figures (Ravec), which authorises security for senior royals on behalf of the Home Office, and was chaired at the time by Sir Richard Mottram.

# Under the committee's regulations, Prince Harry argued, his case should have been put before Ravec's Risk Management Board (RMB), which would have assessed the threats to his and family's security - but that did not happen.

# On Friday, senior judges said the committee had diverged from policy when making its 2020 decision over the prince's security, but concluded it had been "sensible" to do so because of the complexity of his circumstances.

# Prince Harry sat opposite Nada Tawfik
# Prince Harry spoke to BBC News in California following Friday's Court of Appeal ruling in the UK

# Prince Harry said his "jaw hit the floor" when he found out a representative of the Royal Household sat on the Ravec committee, and claimed Friday's ruling had proved its decision-making process was more influenced by the Royal Household than by legal constraints.

# He claimed there had been "interference" by the Royal Household in the 2020 decision, which he said resulted in his status as the most at-risk royal being downgraded to the least at risk "overnight".

# "So one does question how that is even possible and also the motive behind that at the time," he added.

# Prince Harry called on UK Prime Minister Sir Keir Starmer and Home Secretary Yvette Cooper to intervene in his security case, and to overhaul how the Ravec committee operates.

# In a statement released later on Friday, the prince said he would write to Cooper to "ask her to urgently examine the matter and review the Ravec process".

# Additional reporting by Sean Seddon


# """)



# article = {
#     "title": "Prince Harry tells BBC he wants 'reconciliation' with Royal Family",
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

# test agent

import asyncio

from ai_service.llm_loader.llm_ollama import load_llm
from ai_service.agents.talk_organizer import initialize_persona_agent


async def test_agent_executor():
    # Load the raw LLM (not a chain!)
    llm = load_llm("persona")

    # Initialize agent
    agent_executor = await initialize_persona_agent(llm)

    # Query the agent
    user_question = """ what's this mean? Developing and selling video game cheats can be a lucrative business, and video game developers have in recent years had to beef up their anti-cheat teams, whose mission is to ban cheaters, neutralize the software they use, as well as go after cheat developers. """
    result = await agent_executor.ainvoke({"input": {"query": user_question}})
    
    # Output the response
    print("💬 Agent's Final Response:\n", result)

# Run the test
if __name__ == "__main__":
    asyncio.run(test_agent_executor())
