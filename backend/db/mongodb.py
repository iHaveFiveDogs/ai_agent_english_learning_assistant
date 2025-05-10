from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB client setup
client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB_NAME")]
articles_raw = db["articles_raw"]
articles_chunks = db["articles_chunks"]
personas_collection = db["personas"]
