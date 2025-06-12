from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB client setup
client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB_NAME")]
personas_collection = db["personas"]

articles_raw = db["articles_raw"]
articles_chunks = db["articles_chunks"]

novels_raw = db["novels_raw"]
novels_chunks= db["novels_chunks"]

questions_answer_articles = db["questions_answer_articles"]
questions_answer_novels = db["questions_answer_novels"]
questions_answer_dramas = db["questions_answer_dramas"]