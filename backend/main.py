from fastapi import FastAPI

from dotenv import load_dotenv
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from routes.upload_article import router as upload_article_router
from routes.welcome import router as welcome_router
from routes.explain_article import router as explain_article_router
from routes.all_article import router as all_article_router
from routes.agent_langraph_route import router as agent_langraph_router
from routes.dictionary import router as dictionary_router
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

app.include_router(upload_article_router)
app.include_router(welcome_router)
app.include_router(explain_article_router)
app.include_router(all_article_router)
app.include_router(agent_langraph_router)
app.include_router(dictionary_router)

