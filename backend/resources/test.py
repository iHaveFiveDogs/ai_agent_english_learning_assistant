#### to make project file available####
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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

###################### json format test ##############################
# import json

# raw = '{"summary": "Deepankar Rustagi founded OmniRetail in 2022, initially attracting more investment than other sectors, including fintech. Recently, however, industry enthusiasm has diminished due to business model challenges. However, OmniRetail is now receiving $20 million in Series A funding from Norfund, Lagos-based VC firm Timon Capital, and several other investors. This funding will support expansion into Nigeria, Ghana, and Ivory Coast, and deepen its focus on embedded finance. This strategic investment positions OmniRetail to become a dominant force in the African informal retail market, leveraging technology and financial solutions."}'

# parsed = json.loads(raw)
# print(parsed)


##############test upload article######################################################################################################################################
from services.chunk_article_service import upload_article_to_db,clean_content
import asyncio
from db.mongodb import articles_raw
from datetime import datetime
from services.chunk_article_service import clean_content

clean_content = clean_content(""" 
Supporting early-stage entrepreneurs seems to be suddenly in vogue in Europe. Back in March, podcaster and venture investor Harry Stebbings launched Project Europe to great fanfare, aiming to back founders aged 25 and under with a small $10 million fund — riffing on the “Peter Thiel Fellowship” model of yore. Now, a new fund hopes to go one better, this time with $68 million.

EWOR (entrepreneurship without risk) has launched its own “founder fellowship,” committing €60 million. The fund will offer selected founders €500,000 in capital for a 7% stake (in comparison, Project Europe offers €200,000 for a 6.66% stake). EWOR claims that, on average, its alumni have gone on to raise €1 million to €11 million during the fellowship.

Each year, the money will go to 35 entrepreneurs who fit EWOR’s mold of “visionaries, technical prodigies, deeply driven operators, and serial entrepreneurs.” Fellows will get virtual-first support, with 1:1 mentorship (including 1 to 5 hours per week with a “unicorn founder”) and access to 2,000 mentors, VCs, and subject matter experts. The €500,000 investment would comprise €110,000 from EWOR GmbH and an additional €390,000 from the investment fund via an uncapped convertible note or similar instrument.

Founded in 2021, EWOR is run by six entrepreneurs — Daniel Dippold, Alexander Grots, Florian Huber, Petter Made, Quinten Selhorst, and Paul Müller. They previously worked at companies like SumUp, Adjust, ProGlove and United-Domains. 

In an interview with TechCrunch, Dippold contrasted EWOR’s fellowship offering with Project Europe, saying while the latter touted backing entrepreneurs with “just an idea,” EWOR could easily match that offering. “We do two fellowships: ideation and traction. You can literally — like we had a year ago with the youngest machine learning researcher from Cambridge — have no co-founder, no idea. You can start at inception, no problem.”

“We run EWOR like a software company — build, measure, learn … The only thing that matters is it needs to be the most useful thing any founder can possibly do,” he added. 

Ten founders have so far been accepted into this year’s cohort. One of these is U.K.-based Mark Golab, a 3D-printing specialist applying the technology to organ transplants with Cambridge Surgical Models, after surviving a life-threatening infection himself. Another is Vienna-based Viktoria Izdebska, who is working on lead generation with Salesy. 


Previous EWOR fellows include Ricky Knox, who achieved two 9-figure exits with Azimo and Tandem Bank; and Tim Seithe, who bootstrapped and led Tillhub to an exit worth almost €100 million
""")
from services.chunk_article_service import chunk_article, upload_article_to_db
from agents.alfo import alfo_handle_chunked_article_decision


article = {
    "title": "A bigger Project Europe? EWOR launches ‘founder fellowship’ program with $68M",
    "source": "techcrunch.com",
    "upload_date": datetime.utcnow(),
    "content": clean_content
}

if __name__ == "__main__":
    import asyncio

    async def main():
        print("test time:" , datetime.utcnow())
        article_id = await upload_article_to_db(article)
        await chunk_article(article_id)
        await alfo_handle_chunked_article_decision(article_id)

    asyncio.run(main())

# from services.chunk_article_service import upload_article_to_db,clean_content
# import asyncio
# from db.mongodb import articles_raw
# from datetime import datetime
# from services.chunk_article_service import clean_content

# clean_content = clean_content(""" A mysterious investor out of London has asked a bankruptcy judge in Delaware to stop the sale of EV startup Canoo’s assets to its CEO, calling it a “flawed” process.

# Charles Garson, a U.K.-based investor with no obvious ties to the EV startup, offered $20 million for Canoo’s assets, according to a filing. A lawyer representing Garson filed a motion Friday to vacate the sale, claiming he presented a “far superior offer” to that of Canoo CEO Anthony Aquila, who bid just $4 million in cash for the assets. (Aquila’s bid also includes the extinguishment of around $11 million in loans Canoo owes to his own financial firm.)


# Garson allegedly was told by the bankruptcy trustee that his offer would be considered and he had until roughly the end of April to finalize the details, according to the filing. Two days after Garson claims he was told this, the trustee “moved forward with the Sale Hearing” and closed the sale of Canoo’s assets to Aquila. The sale ultimately closed on April 11. The bankruptcy trustee did not respond to a request for comment.

# Garson is not alone in protesting the sale. Harbinger Motors, an EV trucking startup that was created by a number of ex-Canoo employees, objected to the sale before it was finalized. The bankruptcy judge overruled that objection; Harbinger has filed an appeal.

# There is very little information available about Garson online. His LinkedIn profile states he is located in London and involved in real estate investments. He’s listed as a director of a real estate investment company called Garland Holdings Limited in the U.K, according to the country’s business registry.

# The motion to vacate does not explain why Garson is interested in Canoo, or whether other investors are involved. Garson provided a declaration in support of the motion to vacate, which includes 23 exhibits. But all of those documents were filed under seal. A lawyer for Garson did not immediately respond to a request for comment.

# “[Garson] believed he had more than enough time to submit his superior bid based on communications with the Trustee and his counsel. In reliance on such communications, Movant did not object to the sale or formally
# submit a competing bid, all while continuing to finalize his offer and requesting clarifications from the Trustee” according to the filing.

# “Despite a clearly superior offer being practically thrown at him, the Trustee determined to seek Court approval of a transaction” with Aquila, the filing reads. A lawyer for Aquila did not respond to a request for comment.

# As many as eight parties signed NDAs and evaluated Canoo’s assets prior to the sale, a lawyer for the bankrupt startup revealed earlier this month. He said only a few of those came close to making a bid, including one group that the bankruptcy trustee said could raise concerns with the Committee on Foreign Investment in the United States because of its (unspecified) “foreign ownership.” It’s not clear if Garson’s bid is what the trustee was referring to.""")
# from services.chunk_article_service import chunk_article, upload_article_to_db
# from agents.alfo import alfo_handle_chunked_article_decision


# article = {
#     "title": "Mysterious financier asks judge to stop Canoo asset sale",
#     "source": "techcrunch.com",
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
# from agents.word_explainer import precache_ipa_etymology_from_txt
# import asyncio
# import os

# base_dir = os.path.dirname(__file__)
# txt_path = os.path.join(base_dir, "..", "resources", "advanced_chunk_6.txt")  #intermediate_chunk_6,advanced_chunk_5

# if __name__ == "__main__":
#     asyncio.run(precache_ipa_etymology_from_txt(txt_path))



########### precache words######################################################################################################################################

