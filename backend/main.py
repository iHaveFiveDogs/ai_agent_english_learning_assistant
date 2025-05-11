from fastapi import FastAPI

from dotenv import load_dotenv
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routes.learning_tools import router as learning_tools_router
from routes.article_news import router as article_news_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Load environment variables
load_dotenv()

# Configure CORS
origins = [
    "http://localhost:3000",  # React app default port
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(learning_tools_router)
app.include_router(article_news_router)

