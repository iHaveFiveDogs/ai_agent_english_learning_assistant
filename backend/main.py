from fastapi import FastAPI

from dotenv import load_dotenv
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routes.learning_tools import router as learning_tools_router
from routes.content_operator import router as content_operator_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.article_service import cleanup_articles_and_chunks
from datetime import datetime
from fastapi.staticfiles import StaticFiles



app = FastAPI()

scheduler = AsyncIOScheduler()

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
app.include_router(content_operator_router)

# Mount the static directory at /static
app.mount("/static", StaticFiles(directory="static"), name="static")


# @app.on_event("startup")
# async def startup_event():
#     print(f"[Startup] App started at {datetime.now().isoformat()}")
#     # Run once at startup
#     await cleanup_articles_and_chunks()
#     print(f"[Cleanup] Ran cleanup_articles_and_chunks at {datetime.now().isoformat()}")
#     # Schedule daily run
#     scheduler.add_job(
#         lambda: print(f"[Scheduled Cleanup] Running at {datetime.now().isoformat()}") or cleanup_articles_and_chunks(),
#         'interval',
#         days=1
#     )
#     scheduler.start()

